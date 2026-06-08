# Session 022 — 2026-05-31 — правильный фикс «карта ворует тапы» + вернули blur-панель
← [session 021](./session_021_2026-05-31_tabbar-iframe-fix.md)

## Session Intent
s021 (непрозрачная панель) НЕ помог — на части телефонов кнопки нижней панели над картой всё
равно не нажимались. + пользователь хочет вернуть полупрозрачную панель с размытием.

## Root cause (уточнённый)
Кросс-доменный iframe (Яндекс-карта) на ряде браузеров перехватывает touch в своей области
НЕЗАВИСИМО от z-index/непрозрачности оверлея. Поэтому opaque-панель не спасла. Решает только
отключение событий у самого iframe.

## Fix (правильный)
- `.map-frame { pointer-events: none }` на iframe карты → iframe вообще не ловит касания, тапы
  идут к нижней панели и к скроллу страницы на ВСЕХ устройствах.
- Чтобы карта осталась полезной — ссылка-оверлей `<a class="stretched-link">` поверх (открывает
  полные Яндекс.Карты по тапу; это same-origin якорь, тапы не ворует).
- Панель .tabbar ВЕРНУЛИ полупрозрачной с blur (rgba .82 + backdrop-filter saturate+blur,
  -webkit-префикс) — теперь это безопасно, т.к. iframe не перехватывает события.

## Корректировка s021
Заметка s021 «панель должна быть непрозрачной» — НЕВЕРНА/устарела. Реальная причина — iframe,
а не прозрачность. Правильный landmine: карты/виджеты-iframe под фикс-панелью → pointer-events:none.

## What works now (evidence)
- `check` → no issues; `test store` → 13/13 OK; /contacts/ → 200.
- HTML: iframe.map-frame + stretched-link (yandex.ru/maps); CSS: .map-frame pointer-events:none + tabbar backdrop-filter.
- Тач-поведение на «проблемном» устройстве — финально подтверждает пользователь (не воспроизводимо в curl).

## Files changed
- `store/static/store/theme.css` (.tabbar blur вернули; +.map-frame pointer-events:none),
  `store/templates/store/contacts.html` (iframe class map-frame, ссылка-оверлей, контейнер position:relative).

## Session Intent check
Достигнут (механизм фикса точечный). Ждём подтверждение с реального телефона.
