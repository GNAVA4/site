# Session 025 — 2026-05-31 — «Проверить заказ» в меню (ПК + моб.)
← [session 024](./session_024_2026-05-31_order-tracking.md)

## Session Intent
Страница /order/track/ была доступна только из подвала и после оформления. Нужна в основном меню.

## Change
- Добавлена ссылка «Проверить заказ» в десктоп-навигацию (nav-x) и в мобильное меню (гамбургер).
  Теперь доступна из 3 мест: верхнее меню ПК, моб.меню, подвал. [user]

## Evidence
- `check` → no issues; в HTML главной 3 вхождения /order/track/; home/track → 200.

## Files changed
- `store/templates/store/base.html` (2 ссылки в nav).

## Session Intent check
Достигнут.
