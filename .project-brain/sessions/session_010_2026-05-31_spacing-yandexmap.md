# Session 010 — 2026-05-31 — фикс отступа размер/кол-во + Яндекс.Карта в контактах
← [session 009](./session_009_2026-05-31_adblock-banner-fix.md)

## Session Intent
(1) В карточках на главной/категориях размер всё ещё близко к количеству. (2) Встроить
Яндекс.Карту в контакты по конкретному адресу.

## Root cause — отступ
gap стоял на `.pcard__foot`, но размер (.size-field) и кол-во (.buy-row) лежат ВНУТРИ `<form>`,
у которой gap не было → они слипались. Фикс: `.pcard__foot form { display:flex; flex-direction:column; gap:14px; }`.

## Changes
| Изменение | Source |
|-----------|--------|
| `.pcard__foot form` — flex-column gap 14px (реальный отступ размер↔кол-во в карточке) | [user] |
| SiteSettings.address = «Москва, Новомосковский АО, Коммунарка, ТОГК Славянский Мир, ряд Е, 1/8» | [user] |
| contacts.html: интерактивная Яндекс.Карта (map-widget, mode=search&text={{ site.address|urlencode }}, без API-ключа) | [user] |

## What works now (with evidence)
- `check` → no issues; `test store` → 11/11 OK.
- /contacts/ содержит iframe yandex.ru/map-widget с URL-кодированным адресом.

## Files changed
- `store/static/store/theme.css` — `.pcard__foot form` gap.
- `store/templates/store/contacts.html` — Яндекс-карта (iframe) из site.address; fallback если адрес пуст.
- БД: SiteSettings.address = реальный адрес.

## End state
Карта в контактах работает, адрес редактируется в админке (карта следует за ним). Отступ в
карточках исправлен по-настоящему (был на неправильном контейнере). Ждём визуальную проверку.

## Session Intent check
Достигнут.
