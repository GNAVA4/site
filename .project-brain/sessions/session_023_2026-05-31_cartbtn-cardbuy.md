# Session 023 — 2026-05-31 — счётчик корзины белым + компактная покупка в карточке
← [session 022](./session_022_2026-05-31_map-pointerevents-fix.md)

## Session Intent
(1) Счётчик в кнопке корзины (шапка) — белым числом на оранжевом, без белого квадрата-пилюли.
(2) В карточке товара: степпер + кнопка в один ряд (как на ПК), кнопка правее; на телефоне —
та же кнопка, но без текста (только значок корзины).

## Changes
| Изменение | Source |
|-----------|--------|
| Шапка: бейдж счётчика `badge bg-light text-dark` → `fw-bold` (белое число, наследует цвет оранжевой кнопки) | [user] |
| .buy-row: убран flex-wrap → степпер+кнопка всегда в один ряд; степпер компактнее (30px); .btn-add flex:1 справа | [user] |
| Кнопка карточки: `<i cart-plus> <span class="hide-mobile">В корзину</span>` — на ПК текст, на моб. только иконка | [user] |

## What works now (evidence)
- `check` → no issues; `test store` → 13/13 OK; / /catalog/ → 200.
- HTML: счётчик без bg-light; кнопка карточки = иконка + hide-mobile «В корзину».

## Files changed
- `store/templates/store/base.html` (бейдж счётчика), `store/static/store/theme.css` (.buy-row один ряд),
  `store/templates/store/_product_card.html` (кнопка иконка+текст).

## Session Intent check
Достигнут.
