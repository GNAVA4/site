# Session 024 — 2026-05-31 — гостевой трекинг заказа по коду + автоподстановка
← [session 023](./session_023_2026-05-31_cartbtn-cardbuy.md)

## Session Intent
Дать покупателю проверять заказ без аккаунтов/паролей (вариант A) + автоподстановка данных.

## Decision → ADR 002 (гостевой трекинг по коду)

## Changes
| Изменение | Source |
|-----------|--------|
| Order.code (8 симв., алфавит без I/O/0/1; generate_order_code; save() авто-генерит); миграция 0014; бэкафилл 8 заказов | [user] |
| /order/track/ (track_order view): поиск по номер+код, secrets.compare_digest (анти-перебор по таймингу); order_track.html (форма + детали заказа) | [user] |
| Код показан на order_success (№+код, кнопка «Проверить заказ») и в тексте заказа (build_order_text) | [user] |
| Ссылка «Проверить заказ» в подвале; код в админке (readonly, в list/search) | [inferred] |
| Автоподстановка имени/телефона в checkout — localStorage (app.js), НЕ на сервере (приватно) | [user] |

## What works now (evidence)
- makemigrations→0014; migrate OK; backfill 8; `check` → no issues; `test store` → 14/14 OK (+тест трекинга).
- /order/track/ → 200; тест: верный код находит заказ, неверный → «не найден».

## Files changed
- `store/models.py` (Order.code + generate_order_code + save), `store/admin.py` (code),
  `store/views.py` (track_order, import secrets), `store/urls.py` (/order/track/),
  `store/templates/store/order_track.html` (НОВАЯ), `order_success.html` (код+кнопка),
  `store/notifications.py` (код в тексте), `base.html` (ссылка в подвал), `store/static/store/app.js` (автоподстановка),
  `store/tests.py` (+тест), миграция 0014.

## Session Intent check
Достигнут. Трекинг по коду + приватная автоподстановка. Апгрейд до входа по телефону — при желании (ADR 002).
