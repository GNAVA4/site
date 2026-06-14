# Деплой СтройМаг на Ubuntu VPS

Пошаговая установка на чистый Ubuntu LTS (22.04 / 24.04 / 26.04). Стек на сервере:
**nginx → gunicorn (systemd) → Django**, БД — **PostgreSQL (нативно, apt)**, статика собрана
`collectstatic` и отдаётся nginx, HTTPS — Let's Encrypt. Всё приложение живёт в `/opt/shop`.

> Команды с `sudo` выполняются от пользователя с правами sudo. Замени плейсхолдеры:
> `ВАШ_ДОМЕН`, `СИЛЬНЫЙ_ПАРОЛЬ_БД`, `СГЕНЕРИРОВАННЫЙ_КЛЮЧ`.

---

## 0. Предпосылки
- VPS с Ubuntu LTS, есть SSH-доступ (IP + root/sudo).
- Домен, у которого A-запись (`@` и `www`) указывает на IP сервера (нужно для HTTPS).

## 1. Системные пакеты
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-venv python3-pip git nginx postgresql postgresql-client \
                    certbot python3-certbot-nginx
```

## 2. PostgreSQL: база и пользователь
```bash
sudo -u postgres psql <<'SQL'
CREATE DATABASE shop;
CREATE USER shop WITH PASSWORD 'СИЛЬНЫЙ_ПАРОЛЬ_БД';
ALTER ROLE shop SET client_encoding TO 'utf8';
ALTER ROLE shop SET timezone TO 'Europe/Moscow';
GRANT ALL PRIVILEGES ON DATABASE shop TO shop;
ALTER DATABASE shop OWNER TO shop;
SQL
```

## 3. Пользователь приложения и код
```bash
sudo adduser --system --group --home /opt/shop shop
sudo mkdir -p /opt/shop && sudo chown shop:shop /opt/shop
# ВАЖНО: домашняя папка создаётся с правами 750 → nginx (www-data) не сможет отдать /static/ и /media/
# (403 Forbidden). Делаем папку проходимой для остальных:
sudo chmod 755 /opt/shop

# Клонируем под пользователем shop
sudo -u shop git clone https://github.com/GNAVA4/site.git /opt/shop
cd /opt/shop
```

## 4. venv и зависимости
```bash
sudo -u shop python3 -m venv /opt/shop/venv
sudo -u shop /opt/shop/venv/bin/pip install --upgrade pip
sudo -u shop /opt/shop/venv/bin/pip install -r /opt/shop/requirements.txt
```

## 5. Файл окружения `.env`
Сгенерируй секретный ключ:
```bash
/opt/shop/venv/bin/python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```
Создай `/opt/shop/.env` (от пользователя shop) на основе `.env.example`:
```bash
sudo -u shop tee /opt/shop/.env >/dev/null <<'ENV'
DJANGO_SECRET_KEY=СГЕНЕРИРОВАННЫЙ_КЛЮЧ
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=ВАШ_ДОМЕН,www.ВАШ_ДОМЕН
DJANGO_CSRF_TRUSTED_ORIGINS=https://ВАШ_ДОМЕН,https://www.ВАШ_ДОМЕН
DJANGO_SECURE_SSL_REDIRECT=True
DATABASE_URL=postgres://shop:СИЛЬНЫЙ_ПАРОЛЬ_БД@127.0.0.1:5432/shop
DJANGO_CONN_MAX_AGE=60
# Email (если нужен email-канал заказов):
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=shop@ВАШ_ДОМЕН
ENV
sudo chmod 600 /opt/shop/.env
```

## 6. Миграции, статика, администратор
```bash
cd /opt/shop
sudo -u shop bash -c 'set -a; . /opt/shop/.env; set +a; \
  /opt/shop/venv/bin/python manage.py migrate && \
  /opt/shop/venv/bin/python manage.py collectstatic --noinput'
sudo -u shop bash -c 'set -a; . /opt/shop/.env; set +a; /opt/shop/venv/bin/python manage.py createsuperuser'
```

## 7. (Опционально) Перенос данных с локальной машины
Каталог небольшой — можно просто завести всё заново через админку. Либо перенести как есть:

**На локальной машине (Windows PowerShell):** выгрузи данные и скопируй фото.
```powershell
$env:PYTHONUTF8='1'   # ВАЖНО на русской Windows: иначе dump в cp1251 → ошибка
python manage.py dumpdata --natural-foreign --natural-primary `
  --exclude contenttypes --exclude auth.permission --exclude admin.logentry --exclude sessions `
  --indent 2 -o dump.json
# Скопировать на сервер (нужен scp/pscp):
scp dump.json shop@ВАШ_ДОМЕН:/opt/shop/
scp -r media/* shop@ВАШ_ДОМЕН:/opt/shop/media/
```
**На сервере:** загрузи дамп и сбрось sequence.
```bash
cd /opt/shop
sudo -u shop bash -c 'set -a; . /opt/shop/.env; set +a; /opt/shop/venv/bin/python manage.py loaddata dump.json'
sudo -u shop bash -c 'set -a; . /opt/shop/.env; set +a; /opt/shop/venv/bin/python manage.py shell -c "
from django.core.management.color import no_style; from django.db import connection; from django.apps import apps
[connection.cursor().execute(s) for s in connection.ops.sequence_reset_sql(no_style(), list(apps.get_models()))]"'
sudo rm /opt/shop/dump.json   # в дампе ПДн заказов — не хранить
```

## 8. gunicorn как systemd-сервис
```bash
sudo cp /opt/shop/deploy/gunicorn.service /etc/systemd/system/shop.service
sudo systemctl daemon-reload
sudo systemctl enable --now shop
sudo systemctl status shop      # должно быть active (running)
```

## 9. nginx
```bash
sudo cp /opt/shop/deploy/nginx.conf /etc/nginx/sites-available/shop
sudo sed -i 's/ВАШ_ДОМЕН/реальный-домен.ru/g' /etc/nginx/sites-available/shop
sudo ln -sf /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/shop
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl reload nginx
```
Проверь: `http://ВАШ_ДОМЕН` уже должен открываться (по HTTP).

## 10. HTTPS (Let's Encrypt)
```bash
sudo certbot --nginx -d ВАШ_ДОМЕН -d www.ВАШ_ДОМЕН
```
certbot сам добавит 443-блок и редирект с HTTP на HTTPS, и настроит автопродление.

## 11. Бэкапы по расписанию
```bash
chmod +x /opt/shop/deploy/backup.sh
sudo crontab -e
# добавить строку (ежедневно в 3:30):
30 3 * * * /opt/shop/deploy/backup.sh >> /opt/shop/backups/backup.log 2>&1
```
(Дополнительно можно включить бэкапы на стороне провайдера — это снимок всего сервера.)

---

## 🔒 Безопасность (харднинг сервера)

Выполнить один раз после установки.

### Firewall (ufw) — открыть только нужные порты
```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```
PostgreSQL (5432) наружу НЕ открываем — нативный Postgres по умолчанию слушает только localhost.
Проверить, что не торчит в интернет:
```bash
sudo ss -ltnp | grep 5432   # должно быть 127.0.0.1:5432, НЕ 0.0.0.0
```

### SSH: вход по ключу, без root и паролей
Сначала убедись, что зашёл по SSH-ключу (иначе закроешь себе доступ!). Затем в `/etc/ssh/sshd_config`:
```
PermitRootLogin no
PasswordAuthentication no
```
```bash
sudo systemctl restart ssh
```

### fail2ban — защита от перебора (SSH; опц. админка)
```bash
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
```
Базовый jail для SSH включён по умолчанию. Для админки `/admin/` можно добавить jail по логам nginx.

### Авто-обновления безопасности ОС
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Пароли и ключи
- Сменить пароль суперпользователя (перенёсся из dev — слабый): `python manage.py changepassword rus`.
- Пароль БД (`СИЛЬНЫЙ_ПАРОЛЬ_БД`) — длинный случайный, только в `/opt/shop/.env` (chmod 600).
- `DJANGO_SECRET_KEY` — обязателен: приложение откажется стартовать с дефолтным ключом при `DEBUG=False`.

### Бэкапы офсайт
`deploy/backup.sh` хранит дампы на самом сервере. Дополнительно копировать их вовне (снапшоты провайдера
или `rsync` на другое хранилище). В дампах — ПДн клиентов: хранить на РФ-стороне и ограниченно.

### Анти-спам формы заказа
Honeypot уже встроен (скрытое поле). Если пойдёт спам от продвинутых ботов — добавить IP-троттлинг
(`django-ratelimit` + кэш) или капчу.

---

## 🔄 Обновление сайта в будущем

### Изменения в КОДЕ (новые страницы, правки логики/шаблонов/стилей)
Работаешь локально → коммит → push → на сервере подтянуть:
```bash
cd /opt/shop
sudo -u shop git pull
# если менялись зависимости:
sudo -u shop /opt/shop/venv/bin/pip install -r requirements.txt
# если менялись модели (есть новые миграции):
sudo -u shop bash -c 'set -a; . /opt/shop/.env; set +a; /opt/shop/venv/bin/python manage.py migrate'
# если менялись статика/шаблоны со статикой:
sudo -u shop bash -c 'set -a; . /opt/shop/.env; set +a; /opt/shop/venv/bin/python manage.py collectstatic --noinput'
# применить:
sudo systemctl restart shop
```

### Изменения в ДАННЫХ (товары, категории, контент, контакты, удалить/добавить)
Через **админку** `https://ВАШ_ДОМЕН/admin/` в любой момент — деплой не нужен.
Добавить/убрать товары, категории, поменять тексты/цвет/контакты (SiteSettings), загрузить фото.

### Полезные команды
```bash
sudo systemctl restart shop          # перезапуск приложения
sudo systemctl status shop           # статус
journalctl -u shop -f                # логи приложения
sudo nginx -t && sudo systemctl reload nginx   # после правки nginx
```
