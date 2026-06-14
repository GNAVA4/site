# Session 036 — 2026-06-08 — перенос ДАННЫХ SQLite→Postgres (фикс «пустого сайта»)
← [session 035](./session_035_2026-06-08_prod-prep-postgres.md)

## Session Intent
Пользователь: после s035 при локальном запуске пропали все категории/товары/фото/цвет.
Причина — в s035 переключили БД на Postgres и накатили схему, но НЕ перенесли данные (моя недоработка).
Задача: перенести данные из db.sqlite3 в Postgres; объяснить, как запускать локально.

## Диагноз (evidence)
| | cat | prod | img | site | orders |
|---|---|---|---|---|---|
| SQLite (старая) | 9 | 5 | 2 | 1 | 11 |
| Postgres (до) | 0 | 0 | 0 | 1* | 0 |
\*Дефолтный SiteSettings (SiteSettings.load() создал пустой) → стандартный цвет вместо #ed7014.

## Что сделано
1. Временный `config/_sqlite_dump_settings.py` (DATABASES=sqlite, наследует config.settings).
2. `$env:PYTHONUTF8='1'` + `dumpdata --natural-foreign --natural-primary --exclude contenttypes
   --exclude auth.permission --exclude admin.logentry --exclude sessions -o _data_dump.json`.
3. `loaddata _data_dump.json` в Postgres → **Installed 61 object(s)**.
4. Сброс sequence Postgres (connection.ops.sequence_reset_sql) → reset 13 sequences.
5. Удалены временные файлы (_sqlite_dump_settings.py, _data_dump.json, _reset_sequences.py — дамп содержал ПДн).

## Грабли (см. insight)
- `dumpdata -o` на рус. Windows пишет cp1251 → loaddata `UnicodeDecodeError 0xd1`. Фикс: `PYTHONUTF8=1`.
  → insight_2026-06-08_dumpdata-cp1251-windows.

## Результат (evidence)
- Postgres после переноса: cat=9, prod=5, img=2, orders=11, **accent=#ed7014** — совпало с SQLite.
- Локальный запуск: `docker compose up -d` → `venv\Scripts\Activate.ps1` → `python manage.py runserver`.

## Заметки
- Данные теперь в Postgres (volume shop_pgdata). db.sqlite3 — устаревший бэкап (не используется).
- НЕ коммитили: дамп удалён; код приложения в этой сессии не менялся (только данные в БД + insight/session в памяти).

## Session Intent check
Достигнут. Данные восстановлены в Postgres, причина объяснена, дана инструкция запуска.
