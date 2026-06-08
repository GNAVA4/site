# Plan 002: Переделка архитектуры + дизайн (mobile-first) + заказы
_Created session 002 | Status: in-progress (Phase 1 done)_

Goal: современный лаконичный mobile-first магазин; всё редактируемо из админки; статистика;
качественная корзина; выбор канала оформления (Telegram/WhatsApp/Email/Заказ звонка/Позвонить).

Решения: ADR 001 (Order/OrderItem + SiteSettings). Дизайн = Bootstrap 5 + тонкая тема,
акцентный цвет из SiteSettings. Каналы — 5 штук, переключаются в админке.

## Phase 1 — Backend данных  ✅ DONE (session 002)
- [x] SiteSettings (singleton) + Order + OrderItem
- [x] Миграция 0003, applied
- [x] Админка: SiteSettings (singleton), Order (inline позиций, list_editable статус) + статистика (выручка/кол-во/статусы/топ-товары) над списком
- [x] Product admin: list_editable price/stock/is_active
- [x] Evidence: makemigrations/migrate/check OK; смоук-тест синглтона и агрегатов

## Phase 2 — Оформление заказа + корзина  ✅ DONE (session 003)
- [x] context_processor store.context_processors.site → {{ site }} во всех шаблонах
- [x] Корзина: степпер +/− (update_cart, Cart.set_qty/change), удаление, очистка
- [x] Страница оформления checkout.html: OrderForm (имя, телефон, коммент) + радио-каналы (только включённые)
- [x] checkout view создаёт Order+OrderItem (снапшот цен) в transaction.atomic, чистит корзину, PRG → order_success
- [x] Доставка по каналу: telegram deep-link, whatsapp wa.me, email send_mail (dev=console), callback (сохранён), call (tel:)
- [x] order_success.html гейтится по session['last_order'] (анти-перебор id), fallback если реквизит канала пуст
- [x] Валидация: имя+телефон обязательны; выключенный канал отклоняется формой
- [x] Тесты: 8 шт (корзина + чекаут + снапшот цен + singleton) — все зелёные
- [x] Evidence: manage.py test → OK; check --deploy с длинным ключом → 0 issues
- Checkpoint: ревью перед редизайном ← ЗДЕСЬ

## Phase 3 — Mobile-first редизайн  ✅ DONE (session 005, вариант «строгий»)
- [x] theme.css на CSS-переменных (--accent из SiteSettings); шрифты Sora + Hanken Grotesk
- [x] base.html: липкая шапка, нижняя таб-панель (моб.), каталог-offcanvas, подвал из SiteSettings
- [x] _product_card.html (общая карточка), product-grid 2/3/4 кол.
- [x] index (hero из настроек), category, product_detail (липкая buybar на моб.), cart (степпер-карточки), checkout (плиточные каналы), order_success, contacts — все на новых компонентах
- [x] Evidence: check + 10 тестов OK; рендер всех страниц 200; static theme.css отдаётся (200, 13КБ)
- Палитру/шрифты легко сменить (всё в :root) → можно сделать тёплый/минимал-вариант по запросу
> Использовать установленные скиллы (центральная папка SKILLS\.claude\skills\): `frontend-design`
> (избегать «дефолтной AI-эстетики», выразительная типографика, CSS-переменные, анимация) и `theme-factory`
> (10 готовых палитр+шрифтов; для магазина ближе всего modern-minimalist / tech-innovation).
> Свежие практики (веб-поиск s004): mobile ≈70% трафика; цель загрузки <3с; one-page checkout
> снижает abandonment ~20%; touch-target ≥44px; контраст текста ≥4.5:1 (WCAG); body 16–18px,
> line-height 1.4–1.6, 45–75 символов в строке; размеры/наличие показывать явно, не прятать.
- [ ] base.html: тема через CSS-переменные (accent из SiteSettings), шрифт Inter, контейнеры
- [ ] Нижняя таб-панель на мобиле (Главная/Каталог/Корзина/Контакты), бейдж корзины
- [ ] Карточка товара: галерея, степпер, липкая кнопка «в корзину» на мобиле
- [ ] Каталог: аккуратная сетка, фильтр по категориям, пустые состояния
- [ ] Главная: герой из SiteSettings, секции
- [ ] Корзина/чекаут: чистый адаптивный вид
- [ ] Footer/контакты из SiteSettings
- Checkpoint: визуальная проверка пользователем (runserver)

Checkpoints: пауза после каждой фазы.
