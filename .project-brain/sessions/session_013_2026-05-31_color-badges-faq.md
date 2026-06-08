# Session 013 — 2026-05-31 — цвет (сине-стальной+тёплый), бейджи, FAQ, похожие, доработка About
← [session 012](./session_012_2026-05-31_about-icons.md)

## Session Intent
Дизайн-итерация по выбору пользователя: палитра сине-стальная + тёплый акцент; шрифт оставить;
добавить бейджи на товарах, FAQ на главной, похожие товары. + фидбэк по About-странице.

## Changes (with provenance)
| Изменение | Source |
|-----------|--------|
| --ink → сине-стальной #1b2a44; --accent → тёплый #ed7014 (и SiteSettings.accent_color) | [user: цвет «сине-стальной+тёплый»] |
| Шрифт не трогали (Sora+Hanken) | [user] |
| Product.is_hit (бейдж «Хит»); SiteSettings.low_stock_threshold (default 5) → бейдж «Мало осталось»; «Нет в наличии» | [user: бейджи] |
| Бейджи на карточке (overlay) и в детальной (у заголовка) | [user] |
| FAQ-аккордеон на главной (FAQ список в home view) | [user] |
| Похожие товары на стр. товара (та же категория, ≤4) — similar в product_detail | [user] |
| About: about_image (фон-фото в админке); иконки в блоках цифр (.stat__i); «почему мы» → .feature-grid (ровное выравнивание); шаги — номер в строке заголовка (.step__head) | [user-2: фидбэк по About] |

## Magic values
- low_stock_threshold default 5 — вынесен в SiteSettings (редактируется), не хардкод.
- similar [:4], popular [:8] — разумные лимиты витрин.

## What works now (with evidence)
- makemigrations→0009; migrate OK; `check` → no issues; `test store` → 11/11 OK.
- Рендер: / /about/ /catalog/ /product/<id>/ /contacts/ → все 200. accent=#ed7014, отмечен hit-товар.

## Files changed
- `store/models.py` (Product.is_hit; SiteSettings.about_image, low_stock_threshold), `store/admin.py`,
  `store/views.py` (FAQ const + home; similar в product_detail), миграция 0009.
- `store/static/store/theme.css` (--ink/--accent; .badge-*, .pcard__badges; .stat__i; .feature-grid; .step__head; .stats/.steps align).
- `store/templates/store/_product_card.html` (бейджи), `product_detail.html` (бейджи + похожие),
  `index.html` (FAQ-аккордеон), `about.html` (фон-фото, иконки цифр, feature-grid, шаги).

## End state
Палитра стала сине-стальной с тёплыми кнопками; на товарах бейджи; на главной FAQ; на товаре —
похожие; About оформлена блоками с выравниванием. Ждём визуальную проверку (Ctrl+Shift+R).
Для фона About — загрузить about_image в админке.

## Session Intent check
Достигнут (все пункты обеих просьб).
