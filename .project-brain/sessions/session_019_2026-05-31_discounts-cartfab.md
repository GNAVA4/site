# Session 019 — 2026-05-31 — скидки + плавающий виджет корзины + статичная кнопка на моб.
← [session 018](./session_018_2026-05-31_overflow-tabbar.md)

## Session Intent
(1) На моб.карточке товара: кнопка добавления — статичная (как на ПК), вместо липкой панели;
плавающий виджет корзины внизу справа с суммой ₽, тык → корзина.
(2) Скидки, настраиваемые в админке: цена со скидкой + зачёркнутая старая.

## Changes
| Изменение | Source |
|-----------|--------|
| Product.discount_percent (0-95, MaxValueValidator); has_discount/current_retail (округление до рубля); миграция 0012 | [user] |
| Цена со скидкой + зачёркнутая (.price-old) + бейдж −N% (.badge-disc) — карточка и детальная | [user] |
| Корзина/заказ считают по current_retail (Cart.__iter__ sum_retail; OrderItem.price_retail снапшот = current_retail) | [inferred] |
| Тестовые скидки: −20% и −15% на 2 товарах | [user] |
| Моб.: убрал .buybar; кнопка «Добавить» статична (сняли hide-mobile) | [user] |
| Плавающий виджет .cart-fab (моб., внизу справа над таб-панелью, кроме стр. корзины): сумма ₽, тык → корзина | [user] |
| context_processor.site отдаёт cart_count/cart_total; add_to_cart JSON +cart_total; app.js setCartTotal обновляет виджет | [inferred] |

## Note (валюта/округление)
discount применяется к РОЗНИЦЕ (опт без изменений). current_retail округляется ROUND_HALF_UP до
целого рубля (decimal_places=0). Снапшот в заказе хранит фактически списанную (скидочную) цену.

## What works now (evidence)
- makemigrations→0012; migrate OK; `check` → no issues; `test store` → 13/13 OK (+тест скидки).
- Рендер: / /catalog/ /cart/ → 200; в HTML cart-fab, price-old, badge-disc. Скидки −20%/−15% на 2 товарах.

## Files changed
- `store/models.py` (discount_percent + props), `store/admin.py` (discount в list), `store/cart.py` (current_retail),
  `store/views.py` (snapshot current_retail; JSON cart_total), `store/context_processors.py` (cart_count/total),
  `store/static/store/app.js` (setCartTotal), `store/static/store/theme.css` (.cart-fab, .badge-disc, .price-old; убрал .buybar),
  `_product_card.html`/`product_detail.html`/`cart.html` (скидки; статичная кнопка; убран buybar),
  `base.html` (виджет .cart-fab), `store/tests.py` (+тест), миграция 0012.

## Session Intent check
Достигнут. На моб. — статичная кнопка + плавающий виджет с суммой; скидки настраиваются в админке.
