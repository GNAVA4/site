# ADR 005 — PostgreSQL и в dev, и на проде (паритет сред через Docker)

_Date: 2026-06-08 (session 035) · Status: active · Supersedes: «SQLite dev, Postgres потом» из ранних заметок_

## Контекст
Готовим прод. Раньше планировалось: dev на SQLite, прод на Postgres (см. ADR 003, CONTEXT).
Но у проекта есть известная поведенческая разница SQLite↔Postgres, на которой уже спотыкались:
- `insight_2026-06-02_sqlite-cyrillic-icase`: `icontains`/`lower()` по кириллице в SQLite ≠ Postgres;
- по ADR 003 поиск планируется на `pg_trgm`/`SearchVector` — этот код на SQLite вообще не запускается.
Разные БД в dev и prod → риск «у меня работает, на проде сломалось».

## Решение
Использовать **PostgreSQL и локально, и на проде**. SQLite убран полностью.
- Локально Postgres поднимается в Docker (`docker-compose.yml`, образ `postgres:17`, хост-порт **5433**,
  чтобы не конфликтовать с локально установленным Postgres на 5432; volume `shop_pgdata`).
- `settings.py` читает `DATABASE_URL` (парсинг через stdlib `urllib.parse`, без новых конфиг-библиотек —
  держим конвенцию «только os.environ»). Дефолт указывает на dev-контейнер
  `postgres://shop:shop@127.0.0.1:5433/shop`, поэтому локально достаточно `docker compose up -d`.
- На проде `DATABASE_URL` задаётся в окружении (managed или self-hosted Postgres) — переезд = смена одной
  переменной, без правок кода.
- Драйвер — `psycopg[binary]==3.3.4` (Django 6 + psycopg 3).

## Провенанс
Пользователь (s035): «у меня есть докер на компе и постгрес локально, можешь сам поднять контейнер».
Выбор паритета (а не SQLite-fallback в dev) — чтобы ловить БД-специфичные баги до прода, с учётом плана pg_trgm.

## Последствия
- + Полный паритет dev/prod; поиск-апгрейд на `pg_trgm` теперь можно делать и проверять локально.
- + Нет SQLite-специфичных сюрпризов с кириллицей.
- − Для локальной разработки требуется Docker (поднять контейнер БД).
- Тесты гоняются на Postgres: 43/43 OK (s035). `check --deploy` с нормальным ключом → 0 issues.
- Связано: [[adr_003_python-side-search]] (pg_trgm-апгрейд), insight `sqlite-cyrillic-icase` (причина паритета).
