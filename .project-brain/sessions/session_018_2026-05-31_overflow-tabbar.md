# Session 018 — 2026-05-31 — фикс горизонтального вылета + нижняя панель на узких экранах
← [session 017](./session_017_2026-05-31_privacy-security.md)

## Session Intent
На узких устройствах: текст категорий заходит за правый край; нижняя таб-панель «скрывается».

## Root cause
Grid/flex-элементы по умолчанию имеют min-width:auto → не сжимаются уже своего контента. На малых
экранах (≤360px) карточки .cat-grid не помещались в 2 колонки → горизонтальное переполнение,
сдвиг страницы и странное поведение фиксированной нижней панели.

## Fix
| Изменение |
|-----------|
| `.product-grid/.cat-grid/.benefits/.stats/.steps/.feature-grid > * { min-width:0 }` + `.cat-card` min-width:0 + текст overflow-wrap:anywhere — элементы сжимаются, текст переносится |
| body `overflow-x: clip` — страховка от горизонт. вылета (не ломает sticky, в отличие от hidden) |
| Нижняя панель: body padding-bottom `calc(66px + env(safe-area-inset-bottom))` — контент не прячется за панелью на устройствах с home-indicator |

## What works now (evidence)
- `check` → no issues; `test store` → 12/12 OK; / /catalog/ /cart/ → 200; CSS отдаёт overflow-x:clip + min-width:0.

## Files changed
- `store/static/store/theme.css` (только стили).

## Session Intent check
Достигнут (overflow устранён в корне + safe-area). Проверка на реальном узком устройстве — ждём.
