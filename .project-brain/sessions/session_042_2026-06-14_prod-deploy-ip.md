# Session 042 — 2026-06-14 — БОЕВОЙ ДЕПЛОЙ на VPS (по IP, http; домена пока нет)
← [session 041](./session_041_2026-06-14_prod-hardening.md)

## Session Intent
Развернуть сайт на купленном VPS (вариант B — я сам через SSH). Домена пока нет → деплой по IP над http,
HTTPS добавим с доменом позже.

## Сервер
- IP **168.222.202.42**, SpaceWeb, дата-центр СПб (РФ), Ubuntu 26.04 LTS, оформлен на ИП.
- 2 CPU, 3 ГБ RAM, 20 ГБ NVMe (+ swap 2 ГБ создан). Доступ root по SSH-ключу `stroymag-vps`
  (приватный ключ: `C:\Users\rusla\.ssh\id_ed25519`, без passphrase).

## Что развёрнуто (стек по ADR 006)
- Пакеты: python3.14, **PostgreSQL 18.4**, nginx 1.28, certbot, fail2ban, unattended-upgrades.
- БД `shop` + пользователь `shop` (пароль в `/root/.shop_dbpass`, root-only). Postgres слушает только localhost.
- Код: `git clone` репозитория в `/opt/shop` (юзер `shop`), venv, `pip install -r requirements.txt`.
- `/opt/shop/.env` (chmod 600): DEBUG=False, ALLOWED_HOSTS=IP, CSRF=http://IP, **DJANGO_SECURE_SSL_REDIRECT=False,
  DJANGO_SECURE_COOKIES=False** (http-этап!), DATABASE_URL, SECRET_KEY (token_urlsafe(64)). LOG_LEVEL=INFO.
- gunicorn под systemd (`shop.service`, enable --now), nginx (`server_name _`, /static/ + /media/ + proxy:8000).
- Данные перенесены (dumpdata локально + scp + loaddata + sqlsequencereset + scp media): 9 категорий, 3 товара,
  12 заказов, суперюзер **rus** (с локальным паролем). Группа «Менеджеры» (миграция 0017).
- Харднинг: ufw (22/80/443), fail2ban active, unattended-upgrades, бэкап `deploy/backup.sh` в cron (ежедневно 3:30,
  тест-прогон ок: db_*.sql.gz + media_*.tar.gz).

## Код-изменение (закоммичено 6a1f762, до клонирования на сервере)
`config/settings.py`: флаг `DJANGO_SECURE_COOKIES` (default True) гейтит SESSION/CSRF_COOKIE_SECURE + HSTS —
чтобы можно было временно работать по http (без TLS) без поломки cookies/входа. `.env.example` обновлён.

## What works now (evidence)
- Снаружи: `curl http://168.222.202.42/` → **200**, контент рендерится (категории/товары).
- На сервере: gunicorn ACTIVE; nginx 200; `/admin/login/` → 200 (вход по http работает, secure-cookies off).
- Postgres только localhost; ufw active; fail2ban active; бэкап создаёт файлы.
- БД: 9 cat / 3 prod / 12 orders / superuser rus (товаров 3 — столько и в локальной БД, не потеря).

## ОСТАЛОСЬ (важно)
- **Домен + HTTPS**: купить домен → A-запись на 168.222.202.42 → `certbot --nginx` → в `.env` вернуть
  `DJANGO_SECURE_COOKIES=True`, `DJANGO_SECURE_SSL_REDIRECT=True`, ALLOWED_HOSTS/CSRF на домен → restart shop.
- **SMTP** для email-уведомлений о заказах (сейчас не настроен → письма не уходят; заполнить EMAIL_* в .env + SiteSettings.email).
- **SSH**: сейчас вход и по ключу, и по паролю. После бэкапа ключа — отключить PasswordAuthentication.
- Реквизиты ИП в /privacy/; загрузить hero/about фото; офсайт-копия бэкапов.

## Заметки на будущее (эксплуатация)
- Обновление кода: `cd /opt/shop && sudo -u shop git pull` + (опц.) pip/migrate/collectstatic + `systemctl restart shop`.
- Контент/данные — через админку http://168.222.202.42/admin/ (rus).
- Логи приложения: `journalctl -u shop -f`. Перезапуск: `systemctl restart shop`.

## Post-deploy фикс (та же сессия): nginx 403 на статику
- Симптом: сайт без стилей (и админка), фото битые. Причина: `/opt/shop` создалась с правами 750 →
  www-data не проходит в папку → 403 на /static/ и /media/. Фикс: `chmod 755 /opt/shop` +
  `chmod -R a+rX /opt/shop/staticfiles /opt/shop/media`. После — theme/admin/media = 200.
- Внесено в DEPLOY.md §3 (chmod 755 после создания юзера). См. insight_2026-06-14_nginx-403-static-home-perms.

## Session Intent check
Достигнут. Сайт в проде, доступен снаружи по http://168.222.202.42 с реальными данными и СТИЛЯМИ; базовый
харднинг и бэкапы настроены. Следующий шаг — домен и HTTPS.
