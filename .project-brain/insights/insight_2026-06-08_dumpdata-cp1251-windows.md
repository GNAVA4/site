# Insight — смена движка БД требует переноса ДАННЫХ; dumpdata на рус. Windows пишет cp1251

_2026-06-08 (session 036)_

## Контекст
В s035 переключили БД SQLite→PostgreSQL: накатили `migrate` (схему), но НЕ перенесли данные.
Результат: сайт смотрит в пустой Postgres → пропали все категории/товары/фото/акцентный цвет
(SiteSettings создался дефолтным). Данные были целы в `db.sqlite3`.

## Урок 1 — миграция движка ≠ только схема
`migrate` создаёт пустые таблицы. Существующие данные нужно переносить отдельно:
`dumpdata` (из старой БД) → `loaddata` (в новую). При смене движка для проекта С ДАННЫМИ —
всегда планировать перенос данных, не только схему. (Здесь ещё и предупредить пользователя заранее.)

## Урок 2 — dumpdata `-o` на русской Windows пишет cp1251 → loaddata падает
`manage.py dumpdata -o file.json` открывает файл в системной кодировке (cp1251 на рус. Windows),
а JSON-сериализатор Django пишет кириллицу как есть (ensure_ascii=False). Затем
`loaddata` читает файл как UTF-8 → `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd1`.
**ФИКС:** выставить `PYTHONUTF8=1` (PowerShell: `$env:PYTHONUTF8='1'`) перед dumpdata —
Python включает UTF-8 mode, файл пишется в UTF-8, loaddata читает корректно.

## Рабочий рецепт переноса (SQLite→Postgres)
1. Временный settings-модуль, наследующий config.settings, с DATABASES=sqlite (читать старую БД).
2. `$env:PYTHONUTF8='1'`
3. `dumpdata --settings=<temp> --natural-foreign --natural-primary --exclude contenttypes
   --exclude auth.permission --exclude admin.logentry --exclude sessions --indent 2 -o dump.json`
4. `loaddata dump.json` (целевые настройки = Postgres, уже после migrate).
5. Сброс sequence Postgres: `connection.ops.sequence_reset_sql(no_style(), apps.get_models())`
   и выполнить каждый stmt через cursor (иначе новые INSERT конфликтуют по id).
6. Проверить счётчики (тут: cat=9 prod=5 img=2 orders=11, accent=#ed7014 — совпало с SQLite).
7. Удалить временные файлы (дамп содержит ПДн заказов — НЕ коммитить).
