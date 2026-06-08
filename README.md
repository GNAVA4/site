# СтройМаг — интернет-магазин на Django

Небольшой магазин стройтоваров и текстиля: каталог с категориями, корзина в сессии,
оформление заказа через выбранный канал (Telegram / WhatsApp / Email / заказ звонка / «позвоню сам»),
поиск по товарам с учётом опечаток, скидки на товары и категории, гостевой трекинг заказа по коду.
Заказы и все настройки сайта (контент, контакты, каналы, тема) хранятся в БД и редактируются в админке.

## Стек

- **Python 3.12+** (разрабатывался на 3.14)
- **Django 6.0**
- **SQLite** — для разработки (на проде вынести в Postgres)
- **Pillow** — загрузка изображений, **django-cleanup** — удаление старых файлов
- **rapidfuzz** — нечёткий поиск по товарам (кириллица + опечатки)
- Фронт: серверный рендер Django-шаблонов + Bootstrap 5 / FontAwesome (CDN), своя тема на CSS-переменных

## Требования

- Python 3.12 или новее
- pip

## Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/GNAVA4/site.git
cd site

# 2. Создать и активировать виртуальное окружение
python -m venv venv
# Windows (PowerShell):
venv\Scripts\Activate.ps1
# Windows (cmd):
venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate

# 3. Установить зависимости
python -m pip install -r requirements.txt

# 4. Применить миграции (создаст db.sqlite3)
python manage.py migrate

# 5. Создать администратора для входа в админку
python manage.py createsuperuser
```

> База `db.sqlite3` и папка `media/` в репозиторий не входят — после установки сайт пустой.
> Товары, категории и настройки сайта добавляются через админку (см. ниже).

## Запуск

```bash
python manage.py runserver
```

- Витрина: http://127.0.0.1:8000/
- Админка: http://127.0.0.1:8000/admin/

### Первоначальная настройка через админку

1. Войти в `/admin/` под созданным суперпользователем.
2. Открыть **Site settings** (singleton-запись) — задать название, контакты, акцентный цвет,
   включить нужные каналы заказа и заполнить их реквизиты (Telegram-username, WhatsApp-телефон и т.д.).
3. Добавить **категории** и **товары** (с фото и, при желании, скидками и доп. фото галереи).

## Тесты

```bash
python manage.py test
```

## Переменные окружения (для прода)

Локально работают безопасные дефолты (`DEBUG=True`, SQLite, письма в консоль).
Для продакшена задайте через окружение:

| Переменная | Назначение | Пример |
|------------|-----------|--------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django (обязательно на проде!) | длинная случайная строка |
| `DJANGO_DEBUG` | Режим отладки | `False` |
| `DJANGO_ALLOWED_HOSTS` | Разрешённые хосты (через запятую) | `example.com,www.example.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Доверенные origin для CSRF по HTTPS | `https://example.com` |
| `DJANGO_SECURE_SSL_REDIRECT` | Принудительный редирект на HTTPS | `True` |
| `EMAIL_HOST` / `EMAIL_PORT` | SMTP-сервер | `smtp.yandex.ru` / `587` |
| `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | Логин/пароль SMTP | — |
| `EMAIL_USE_TLS` | TLS для SMTP | `True` |
| `DEFAULT_FROM_EMAIL` | Адрес отправителя | `shop@example.com` |

При `DEBUG=False` автоматически включаются HSTS, secure-cookies, SSL-redirect и пр.

### Чек-лист продакшена

```bash
python manage.py collectstatic   # собрать статику в staticfiles/
python manage.py check --deploy  # проверка прод-настроек безопасности
```

- Вынести БД на Postgres (тогда же поиск можно перевести на `pg_trgm`/`SearchVector`).
- Bootstrap/FontAwesome подключаются с `cdnjs.cloudflare.com` (jsdelivr и Google Fonts CDN
  нестабильны в РФ). Для прода предпочтительно захостить ассеты локально.

## Структура

```
config/   — настройки проекта (settings, urls, wsgi)
store/    — приложение магазина
  models.py    — SiteSettings, Category, Product, ProductSize, ProductImage, Banner, Order, OrderItem
  views.py     — вьюхи (каталог, карточка, поиск, корзина, оформление, трекинг)
  cart.py      — корзина в сессии
  search.py    — поиск по товарам (Python-side, rapidfuzz)
  listing.py   — витрина: фильтры / сортировка / пагинация
  admin.py     — админка + статистика заказов
  static/store/theme.css — дизайн-система (CSS-переменные)
  templates/store/       — шаблоны
media/    — загруженные изображения (не в репозитории)
```
