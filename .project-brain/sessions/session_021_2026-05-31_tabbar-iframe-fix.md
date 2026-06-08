# Session 021 — 2026-05-31 — фикс: карта перекрывала нижнюю панель + решение по ПДн
← [session 020](./session_020_2026-05-31_optdiscount-widget-anim.md)

## Session Intent
(1) Решение по хранению ПДн. (2) Баг: на стр. Контакты (моб.) Яндекс-карта перекрывала нижнюю
таб-панель — тапы по «Главная» и т.п. над картой не срабатывали.

## Decisions
- ПДн: ВАРИАНТ A — данные храним (имя/телефон/коммент в Order). Согласие + /privacy/ остаются. [user]
  → закрывает открытый вопрос из session_017.

## Bug fix
Причина: у .tabbar был полупрозрачный фон + backdrop-filter:blur. blur НЕ работает поверх
кросс-доменного iframe (Яндекс-карта) → карта в зоне перекрытия композитится ВЫШЕ панели и
перехватывает touch. Фикс: фон панели сделан НЕПРОЗРАЧНЫМ (#fff, без backdrop-filter) + лёгкая
верхняя тень. Непрозрачный positioned-элемент с z-index 1040 надёжно ловит тапы поверх iframe.

## What works now (evidence)
- `check` → no issues; /contacts/ → 200; в CSS .tabbar background:#fff (без blur).

## Files changed
- `store/static/store/theme.css` — .tabbar: background #fff, убран backdrop-filter, +box-shadow.

## Note / landmine
НЕ возвращать backdrop-filter/прозрачность на .tabbar — ломает тапы над картой. То же правило для
любых фикс-оверлеев поверх iframe: делать непрозрачными.

## Session Intent check
Достигнут. Открытых вопросов по ПДн больше нет (выбран A).
