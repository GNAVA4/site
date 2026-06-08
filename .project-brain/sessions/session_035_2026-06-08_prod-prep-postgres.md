# Session 035 — 2026-06-08 — прод-подготовка: PostgreSQL (dev+prod), WhiteNoise, gunicorn, чистка
← [session 034](./session_034_2026-06-08_readme-git-init.md)

## Session Intent
Начать подготовку к проду. Дал пользователю полный список (блокеры/важное/желательное/решения).
Решения: хостинг — пока не выбран (советую РФ VPS); БД — Postgres (решил за пользователя); юр.лицо есть.
Пользователь выбрал ПАРИТЕТ: Postgres и локально (Docker), и на проде. Эта сессия = Партия 1 (код, не
зависящий от площадки).

## Changes
| Изменение | Source |
|-----------|--------|
| `docker-compose.yml` (НОВЫЙ): postgres:17, хост-порт 5433, volume shop_pgdata, healthcheck | [user] |
| `config/settings.py`: DATABASES из `DATABASE_URL` (парсинг urllib.parse), ENGINE=postgresql, дефолт на dev-контейнер; SQLite убран; CONN_MAX_AGE из env | [user, ADR 005] |
| `requirements.txt`: +`psycopg[binary]==3.3.4`, +`whitenoise==6.12.0`, +`gunicorn==26.0.0` | [user] |
| `config/settings.py`: WhiteNoiseMiddleware (после SecurityMiddleware) + `STORAGES` (CompressedManifestStaticFilesStorage для статики) | [user] |
| `.env.example` (НОВЫЙ): все прод-переменные (SECRET_KEY/DEBUG/ALLOWED_HOSTS/CSRF/DATABASE_URL/EMAIL_*) | [user] |
| Чистка: убран `settings.TELEGRAM_MANAGER` (мёртвое наследие, дефолт-хэндл был публичен); удалён `store/templates/store/product_list.html` (мёртвый шаблон, нигде не используется — проверено grep) | [user, OPEN TODO] |
| `README.md`: обновлён под Postgres/Docker (стек, шаги установки `docker compose up -d`, env-таблица +DATABASE_URL, чек-лист прода +gunicorn) | [user] |

## Решения сессии
- **ADR 005**: PostgreSQL и в dev (Docker), и на проде — паритет сред. Причина: SQLite↔Postgres
  расходятся по кириллице (insight) + план pg_trgm (ADR 003) на SQLite не идёт. SQLite убран.
- Конфиг БД через `DATABASE_URL` + stdlib-парсер (без django-environ — держим конвенцию os.environ).
- WhiteNoise для статики (раздача приложением, без обязательного nginx-локейшна под статику).

## What works now (evidence)
- Docker: `docker compose up -d --wait` → `Container shop_postgres ... Healthy`, порт 5433.
- `manage.py migrate` на Postgres → все 16 миграций store + системные OK.
- `manage.py test` на **Postgres** → **43/43 OK** (паритет подтверждён; кириллица-поиск работает).
- `manage.py collectstatic --noinput` (WhiteNoise manifest) → 132 файла, post-processed, без ошибок.
- `manage.py check --deploy` (DEBUG=False + прод-env + сгенерированный ключ) → **0 issues**.
  (Промежуточный прогон с фиктивным ключом 'aaaa…' дал security.W009 — это артефакт ключа из 1 символа,
  не настоящая проблема; с get_random_secret_key() чисто.)

## Landmines / заметки
- Dev-БД теперь требует Docker: `docker compose up -d` перед migrate/runserver.
- Порт 5433 (не 5432) — намеренно, чтобы не конфликтовать с локальным Postgres пользователя.
- `STORAGES` = CompressedManifestStaticFilesStorage: после правок статики нужен `collectstatic`;
  в dev (DEBUG=True) manifest обходится, тесты не падают. Прод: обязателен collectstatic.
- Дефолтный `DATABASE_URL` содержит dev-пароль shop/shop — локальный, не секрет (как django-insecure key).
- `db.sqlite3` в корне остался (gitignore), но БОЛЬШЕ НЕ ИСПОЛЬЗУЕТСЯ — можно удалить вручную.

## НЕ сделано (вынесено на решение пользователя)
- **Bootstrap/FontAwesome локально** вместо cdnjs — НЕ делал. Причина: в base.html:9 коммент самого
  проекта «cdnjs стабильно работает в РФ»; вендоринг (≈5 МБ webfonts FA + переписывание url() под manifest)
  — тяжёлый и НЕблокер. Вынесено на явное решение (оставить cdnjs vs вендорить).
- **Партия 2** (зависит от площадки/данных): реквизиты ИП в /privacy/; nginx+systemd+TLS+бэкап-скрипт+
  инструкция деплоя под выбранный VPS; реальные SiteSettings через админку.

## Session Intent check
Партия 1 (код, hosting-agnostic) выполнена и проверена: Postgres-паритет, WhiteNoise, gunicorn, env-шаблон,
чистка. Осталось: решение по ассетам (Партия 1, опц.) и Партия 2 после выбора хостинга.
