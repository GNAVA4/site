# Session 030 — 2026-06-03 — requirements.txt (фиксация зависимостей)
← [session 029](./session_029_2026-06-03_discount-badge-cosmetic.md)

## Session Intent
Закрыть OPEN-задачу: зависимости стояли только в venv, манифеста не было. Завести requirements.txt.

## Change
Создан `requirements.txt` в корне с ПРЯМЫМИ зависимостями, пинованными под установленные версии:
Django==6.0.2, pillow==12.1.0, django-cleanup==9.0.0, rapidfuzz==3.14.5. Транзитивные
(asgiref, sqlparse, tzdata) не фиксируем — pip подтянет совместимые. [user]

## Evidence
- Версии сверены с `pip freeze` venv — совпадают (asgiref 3.11.1, Django 6.0.2, django-cleanup 9.0.0,
  pillow 12.1.0, RapidFuzz 3.14.5, sqlparse 0.5.5, tzdata 2025.3).
- Установка/восстановление окружения: `python -m pip install -r requirements.txt`.
- Полную переустановку в чистый venv не гоняли (сеть; манифест проверен сверкой версий).

## Files changed
- `requirements.txt` — НОВЫЙ.

## Session Intent check
Достигнут. Окружение теперь воспроизводимо из манифеста.
