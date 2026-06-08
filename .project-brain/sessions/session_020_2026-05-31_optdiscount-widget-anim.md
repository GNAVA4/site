# Session 020 — 2026-05-31 — скидка на опт (настраиваемо) + анимация виджета + виджет на ПК
← [session 019](./session_019_2026-05-31_discounts-cartfab.md)

## Session Intent
(1) Скидку применять и к опту — управляемо в админке (розница/опт/обе). (2) Виджет корзины:
анимация выезда справа. (3) Виджет также на ПК.

## Changes
| Изменение | Source |
|-----------|--------|
| Product.discount_target (TextChoices: retail/wholesale/both, default retail); миграция 0013 | [user] |
| current_wholesale + retail_discounted/wholesale_discounted; _discounted() helper | [user] |
| Корзина sum_wholesale и заказ OrderItem.price_wholesale — по current_wholesale | [inferred] |
| Шаблоны: опт показывает current_wholesale + зачёркнутый старый, если wholesale_discounted (карточка/детальная/корзина) | [user] |
| Виджет .cart-fab: hidden→is-shown через transform translateX(140%)→0 (выезд справа, cubic-bezier); prefers-reduced-motion | [user] |
| Виджет показывается и на ПК (убрал hide-desktop / display:none; desktop bottom:24px, моб. над таб-панелью) | [user] |
| app.js: setCartTotal toggles .is-shown (вместо display) | [user] |
| Демо: 1 товар скидка на BOTH (опт тоже), 1 — только розница | [user] |

## What works now (evidence)
- makemigrations→0013; migrate OK; `check` → no issues; `test store` → 13/13 OK.
- Демо: −20% both (1000000→800000, опт 1000→800); −15% retail (опт 450 без изменений).
- CSS отдаёт is-shown + translateX (анимация); home 200.

## Files changed
- `store/models.py` (discount_target + current_wholesale + helpers), `store/admin.py` (discount_target в list),
  `store/cart.py` (current_wholesale), `store/views.py` (snapshot current_wholesale),
  `store/static/store/theme.css` (.cart-fab анимация + ПК), `store/static/store/app.js` (is-shown toggle),
  `base.html` (виджет is-shown, без hide-desktop), `_product_card`/`product_detail`/`cart` (опт-скидка), миграция 0013.

## Session Intent check
Достигнут. Скидка гибко (розница/опт/обе); виджет выезжает справа и на ПК, и на моб.
