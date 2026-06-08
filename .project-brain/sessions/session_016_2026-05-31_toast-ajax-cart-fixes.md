# Session 016 — 2026-05-31 — AJAX-корзина с toast + фиксы моб.корзины и нижней панели
← [session 015](./session_015_2026-05-31_more-icons.md)

## Session Intent
3 бага с мобилки: (1) кнопка удаления в корзине вылезает за бокс на узких экранах; (2) добавление
в корзину перекидывает в начало страницы (ради сообщения) — нужен toast без перезагрузки; (3) нижняя
таб-панель «проскакивает» при инерционном скролле.

## Fixes
| Баг | Причина | Фикс |
|-----|---------|------|
| Удалить вылезает за бокс | `.cart-row__ctl` имел width:100% + margin-left:86px → переполнение | margin-left:0 на моб., gap 8, stepper 36px, .cart-line-total nowrap |
| Прыжок в начало при добавлении | POST→redirect→GET (для message) перезагружал страницу | AJAX: формы .js-add отправляются fetch'ем; вью отдаёт JSON при X-Requested-With; toast + обновление бейджа без перезагрузки. Без JS — старый redirect (фолбэк) |
| Нижняя панель дёргается | iOS rubber-band + background-attachment:fixed | body overscroll-behavior-y:none; на моб. background-attachment:scroll; .tabbar translateZ(0)/will-change/backface-hidden |

## New: toast
- `#toastHost` (fixed; десктоп сверху-справа, моб. снизу над таб-панелью). showToast(text,kind) —
  компактный, авто-скрытие 3.5с, крестик. Бейдж корзины (.js-cart-count) всегда в DOM (скрыт при 0),
  обновляется JS из cart_count.

## What works now (evidence)
- `check` → no issues; `test store` → 11/11 OK.
- AJAX add → 200 application/json {ok, message, cart_count}; не-AJAX add → 302 (redirect-фолбэк).

## Files changed
- `store/static/store/app.js` — showToast, setCartCount, перехват submit form.js-add (fetch).
- `store/static/store/theme.css` — .toast-host/.toastx; фиксы .cart-row__ctl (моб.); body overscroll + bg-attachment моб.; .tabbar GPU-слой.
- `store/templates/store/base.html` — #toastHost; бейджи .js-cart-count (всегда в DOM).
- `store/templates/store/_product_card.html`, `product_detail.html` — class js-add на формах.
- `store/views.py` — add_to_cart: JsonResponse при AJAX (импорт JsonResponse), иначе messages+redirect.

## End state
Добавление в корзину — мгновенный toast без прыжка наверх; моб.корзина не переполняется; нижняя
панель стабильна. Ждём проверку на реальном устройстве.

## Session Intent check
Достигнут (все 3 бага).
