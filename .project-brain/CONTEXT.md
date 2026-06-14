# PROJECT CONTEXT — my_shop («СтройМаг»)
_Updated: 2026-06-08 session 034_

## What this project is
Небольшой Django-магазин стройтоваров/текстиля: каталог, корзина в сессии, оформление
заказа через выбранный канал (Telegram/WhatsApp/Email/Заказ звонка/Позвонить). Заказы и все
настройки (контент, контакты, каналы) — в БД, редактируются и видны со статистикой в админке.

## Stack
Python + Django 6.0.2, **PostgreSQL 17** (dev в Docker + прод — паритет, ADR 005; psycopg 3),
Pillow, django-cleanup, **WhiteNoise** (статика) + **gunicorn** (прод-сервер), Bootstrap 5 (CDN; тонкая
тема). Конфиг и email — через os.environ (без django-environ); БД — через DATABASE_URL (stdlib-парсер).

## Current state
Функционально полный: главная, каталог, карточка, корзина со степпером (+/−), оформление
(форма имя/телефон/коммент + радио-каналы из включённых в SiteSettings), создание Order/OrderItem
со снапшотом цен в транзакции, страница успеха с действием под канал, email в dev → консоль.
Админка: заказы (inline, статусы, статистика), товары, SiteSettings. 8 автотестов зелёные,
`check --deploy` чист. 10 тестов зелёные. **Внешний вид (s005): новый mobile-first редизайн —
строгая тема на CSS-переменных (Sora+Hanken Grotesk, акцент из SiteSettings), липкая шапка,
нижняя таб-панель + offcanvas-каталог на моб., липкая buybar на карточке, степпер в корзине.**
Все 3 фазы plan_002 закрыты.
**Поиск (s026):** поиск по всем товарам (название+описание+категория) на стороне Python —
кириллица+опечатки через rapidfuzz; страница /search/ + поле в шапке + «Поиск» в моб.меню. ADR 003.
**Витрина (s031–032):** простые фильтры (сортировка + «в наличии»/«со скидкой») на каталоге/категории;
РАСШИРЕННЫЕ фильтры (категория/цена/в наличии/скидка/хиты/сортировка+релевантность) — в ПОИСКЕ,
на телефоне выезжающей offcanvas-панелью с «Применить» (_search_filters.html). Пагинация (PAGE_SIZE=12).
Раздел «Скидки» /sale/ УБРАН (s032) — фильтр «со скидкой» в общих фильтрах. Галерея фото товара (ProductImage).

## Active work
plan_002 завершён (все 3 фазы). Открыто: визуальная проверка пользователем; опционально —
альтернативные палитры, прод-БД/collectstatic, поиск, slug/SEO.
**Git (s034):** проект под git, запушен на https://github.com/GNAVA4/site.git (ветка `main`,
первый коммит 2db2b1d, без Claude в соавторах). Есть `README.md` и `.gitignore`. В репо НЕ входят
`venv/`, `db.sqlite3`, `media/`, `staticfiles/`, логи, `.env*` → свежий клон = пустой сайт
(docker compose up + migrate + createsuperuser + админка). `.project-brain/` и `CLAUDE.md` намеренно в репо.
**🚀 ПРОД (s042):** сайт развёрнут на VPS **http://168.222.202.42** (Ubuntu 26.04, СПб, ИП). Стек: nginx →
gunicorn (systemd `shop.service`) → Django → PostgreSQL 18. Код в `/opt/shop` (юзер shop), доступ root по
SSH-ключу. Данные перенесены (9 cat/3 prod/12 orders, суперюзер rus). ufw+fail2ban+бэкап-cron+swap. Детали —
STATE.prod / session_042. ⚠️ Этап IP/HTTP: `DJANGO_SECURE_COOKIES=False`, `DJANGO_SECURE_SSL_REDIRECT=False` в
`/opt/shop/.env` — при добавлении домена+TLS вернуть True. ⚠️ SMTP не настроен → email о заказах НЕ уходят
(заполнить EMAIL_* + SiteSettings.email). Обновление: `cd /opt/shop && sudo -u shop git pull` + restart shop.
⚠️ Права (s042): `/opt/shop` ДОЛЖНА быть 755 (иначе nginx 403 на /static//media/ — папка системного юзера
создаётся 750). Не понижать. См. insight_2026-06-14_nginx-403-static-home-perms.

**Прод-подготовка Партия 1 (s035):** SQLite→PostgreSQL (dev в Docker, `docker-compose.yml` порт 5433;
прод через `DATABASE_URL`; ADR 005), psycopg 3, WhiteNoise+gunicorn, `.env.example`. Чистка: убраны
TELEGRAM_MANAGER и product_list.html. 43/43 тестов на Postgres, `check --deploy` 0 issues. ОСТАЛОСЬ:
решение по вендорингу Bootstrap/FA; Партия 2 (nginx/systemd/TLS/бэкап/деплой) — после выбора хостинга.

## Decisions that affect ALL code
- Заказы сохраняются в БД (Order/OrderItem, снапшот цен); канал = лишь уведомление [user, ADR 001]
- SiteSettings — singleton pk=1: контакты/каналы/тема/тексты; доступ SiteSettings.load(); во всех
  шаблонах как {{ site }} (context processor) [inferred]
- Включённые каналы заказа задаются булевыми флагами в SiteSettings; форма показывает только их [user]
- checkout: PRG (POST→redirect order_success); success гейтится session['last_order'] [inferred]
- Каналы (s004): значения telegram/whatsapp/email/callback/call; ЛЕЙБЛЫ — Telegram/WhatsApp/Email/
  «Позвоните мне»/«Позвоню сам». Email = mailto клиента + серверная отправка резервом. «Позвоню сам»
  на success показывает контакты магазина (тел/почта/часы/адрес) [user]
- Телефон в чекауте: +7 — статичный префикс (input-group), пользователь вводит остаток; +7
  добавляется на сервере (clean_customer_phone), если номер не начинается с '+' [user, s004]
- Email: dev=console backend, прод=SMTP из env [user]
- Уведомление магазина о НОВОМ заказе (s040): send_order_email шлёт на SiteSettings.email при ЛЮБОМ
  канале (а не только при email-канале), со ссылкой на заказ в админке; сбой логируется, оформление не
  ломает. Владелец узнаёт о заказе независимо от того, нажал ли клиент дип-линк на success [user]
- Корзина: session['cart']={"id:size":{...}}, ключ непрозрачный, НЕ парсить; мутации только POST [inferred, s001]
- Опт и розница показываются ОБЕ; порог «от 10 шт» в коде НЕ применяется [user]
- Поиск — на стороне Python (store/search.py), НЕ в SQL: rapidfuzz-Левенштейн ловит опечатки.
  Изначально ещё и потому, что SQLite не умел регистр кириллицы. Теперь БД=Postgres → апгрейд на
  pg_trgm/SearchVector стал возможен (опц., при росте каталога) [user, ADR 003/005]
- БД — **PostgreSQL и в dev (Docker), и на проде** (паритет, SQLite убран). Конфиг из `DATABASE_URL`
  (settings._database_config, stdlib-парсер; дефолт = dev-контейнер postgres://shop:shop@127.0.0.1:5433/shop).
  Локально: `docker compose up -d`. На проде DATABASE_URL из env [user, ADR 005]
- Статику на проде отдаёт WhiteNoise (STORAGES=CompressedManifestStaticFilesStorage); прод-сервер gunicorn [s035]
- Скидки (s028): СВОЯ скидка товара важнее скидки категории и НЕ суммируется. Считать только через
  Product.effective_discount_percent/effective_discount_target (не через сырой discount_percent).
  current_retail/current_wholesale учитывают обе → корзина/заказ/снапшот корректны [user, ADR 004]

## Known landmines ⚠️
- НЕ парсить ключ корзины split('_') — был источник 500 (insight cart-string-key)
- add/remove/clear/update корзины и checkout-каналы — мутации только POST (@require_POST/форма)
- SiteSettings — singleton: save() форсит pk=1; всегда брать SiteSettings.load()
- OrderItem хранит СНАПШОТ цены/названия — не путать с живой ценой Product
- order_success доступен только владельцу (session['last_order']); перебор id не выдаёт чужой заказ
- Test Client в обычном `manage.py shell` → DisallowedHost 'testserver'; проверять в `manage.py test`
  или с SERVER_NAME='localhost'
- Если канал включён, но реквизит (telegram_username/whatsapp_phone) пуст → на success показывается
  fallback-текст, не ссылка. Заполнять реквизиты в админке.
- ⚠️ Авто-уведомление о заказе (s040) уходит на SiteSettings.email. Пусто → письма НЕ будет (warning в лог).
  На проде нужен рабочий SMTP (EMAIL_* в env) И заполненный «Email для заказов» в админке.
- settings.TELEGRAM_MANAGER УДАЛЁН (s035) — было мёртвое наследие. Не возвращать.
- Дефолтный SECRET_KEY — только dev; прод требует длинный DJANGO_SECRET_KEY. ⚠️ репо публичный (s034):
  django-insecure-дефолт открыт. С s041 приложение ОТКАЗЫВАЕТСЯ стартовать при DEBUG=False с дефолтным
  ключом (raise ImproperlyConfigured) — на проде DJANGO_SECRET_KEY из env ОБЯЗАТЕЛЕН.
- ⚠️ Honeypot (s041): OrderForm имеет скрытое поле `website` (ловушка от ботов). Оно ДОЛЖНО рендериться в
  checkout.html (в скрытом блоке) — не удалять, не делать required. Заполнено → заказ отклоняется как спам.
- Логи (s041): уровень из env `DJANGO_LOG_LEVEL` (дефолт INFO; dev может DEBUG). На проде не ставить DEBUG.
- Git (s034): `.gitignore` исключает venv/db.sqlite3/media/staticfiles/логи/.env*/.idea. НЕ коммитить
  эти пути. Remote origin = github.com/GNAVA4/site, ветка main.
- ⚠️ БД=Postgres (s035): для ЛОКАЛЬНОЙ разработки нужен Docker — `docker compose up -d` перед migrate/
  runserver/test. Порт хоста 5433 (НЕ 5432, чтобы не конфликтовать с локальным Postgres). SQLite убран.
- ⚠️ STORAGES=CompressedManifestStaticFilesStorage (WhiteNoise): после правок статики на проде нужен
  `collectstatic`. В dev (DEBUG=True) manifest обходится — тесты/runserver не падают.
- product_list.html УДАЛЁН (s035, был мёртвый). db.sqlite3 в корне больше не используется (можно удалить).
- SQLite — dev; для прода вынести БД. product_list.html — мёртвый шаблон.
- Тема (s005) на CSS-переменных в theme.css :root; --accent приходит из SiteSettings.accent_color
  (inline <style> в base.html). Менять палитру/шрифты — там же, не в разметке. Шрифты с Google Fonts CDN.
  Bootstrap оставлен для сетки/утилит/JS (dropdown/carousel/offcanvas); свой вид поверх в theme.css.
- Прод: не забыть collectstatic (STATIC_ROOT уже задан).
- ПДн (s021): решение = ВАРИАНТ A — данные (имя/телефон/коммент) ХРАНИМ в Order. Согласие
  (OrderForm.consent) + страница /privacy/ обязательны. Не удалять их.
- ⚠️ iframe под фикс-панелью (s022, ВАЖНО): кросс-доменный iframe (Яндекс-карта) перехватывает
  touch в своей области независимо от z-index → нижняя панель не ловит тапы. ФИКС: iframe карты
  имеет `.map-frame { pointer-events:none }` + ссылка-оверлей (stretched-link) для открытия полной
  карты. Панель .tabbar при этом МОЖЕТ быть полупрозрачной с blur (вернули). НЕ убирать
  pointer-events:none у .map-frame. (s021-заметка про «непрозрачную панель» — устарела, не сработала.)
- ⚠️ Блокировщики рекламы (s009): НЕ использовать слово «banner»/«ad»/«popup» в путях медиа,
  URL, id или class — uBlock/AdBlock режут (blocked:other) и прячут такие элементы. Папка фото
  слайдера = `media/promo/`, id=promoCarousel, класс .promo-slide. Модель называется Banner (в HTML
  не попадает — ок). См. insight_2026-05-31_adblock-banner-path.
- CDN (s005): использовать ТОЛЬКО cdnjs.cloudflare.com (Bootstrap+FA). jsdelivr/fonts.googleapis
  режутся в РФ и блокируют отрисовку → «стили не применяются». Google Fonts грузятся неблокирующе.
  См. insight_2026-05-31_cdn-jsdelivr-ru-block. Для прода лучше захостить Bootstrap локально.
- ⚠️ SQLite + кириллица (s026): `icontains`/`lower()` регистронезависимы ТОЛЬКО для латиницы.
  Регистронезависимый поиск/сравнение по кириллице делать в Python (str.lower()), не в SQL.
  См. insight_2026-06-02_sqlite-cyrillic-icase. На Postgres проблемы нет.
- Зависимости (s030): `requirements.txt` в корне (Django/pillow/django-cleanup/rapidfuzz, прямые,
  пинованы). Восстановление окружения: `python -m pip install -r requirements.txt`.
- Поиск грузит активные товары в память (O(товаров×слов)) — ок для сотен SKU, не для десятков тысяч.
- Витрина (s031–032): сортировка по цене — по БАЗОВОЙ price_retail (current_* считается в Python).
  PAGE_SIZE=12 в listing.py. Простые фильтры каталога/категории НЕ содержат поля цены НАМЕРЕННО (это
  был источник горизонт. переполнения и дёрганья таб-панели) — цена только в расширенных фильтрах поиска.
  Поиск по умолчанию сортируется по релевантности (Case/When по rapidfuzz-порядку через browse(relevance_pks)).
- Раздел «Скидки» /sale/ УБРАН (s032). НЕ возвращать как отдельную страницу — это фильтр «со скидкой» (sale=1).
- Страница /search/ (s033): БЕЗ запроса = режим browse (все товары + фильтры); с запросом = results; нет совпадений = empty (похожие/пусто). Фильтры показываются в browse и results.
- ⚠️ Responsive offcanvas (.offcanvas-lg): кнопкам data-bs-dismiss/btn-close НУЖЕН data-bs-target="#id" — иначе крестик не закрывает (Bootstrap ищет .offcanvas, не .offcanvas-lg).
- ⚠️ Django {# … #} — только ОДНОСТРОЧНЫЕ; многострочный комментарий рендерится как текст на странице.
- Галерея (s031): обложка = Product.image; доп.фото = ProductImage (related_name='images'); карусель
  на странице товара только при >1 фото; Product.gallery = обложка + доп. по полю sort.
- Моб.шапка (s027): корзины в шапке на ТЕЛЕФОНЕ нет НАМЕРЕННО (она в нижней таб-панели + в бургер-меню);
  вместо неё — кнопка поиска (hide-desktop → /search/). На ПК корзина в шапке есть (hide-mobile). Не «чинить».

## Key file map
- `store/models.py` — SiteSettings, Order, OrderItem, Product, Category, ProductSize, Banner
- `store/views.py` — FBV: home/catalog/category/product/**search** + cart/update(qty+size)/checkout/order_success; F() просмотры
- `store/search.py` — поиск по товарам: нормализация регистра в Python, rapidfuzz-Левенштейн, балльное ранжирование (AND + «похожие»)
- `store/listing.py` — витрина: browse() фильтры (в наличии/скидка/хит/категория/цена)+сортировка(+релевантность для поиска)+пагинация (PAGE_SIZE=12, SALE_Q). Партиалы `_browse_controls.html` (простые), `_search_filters.html` (расширенные, offcanvas), `_pager.html`
- Страницы (s007): /catalog/ — все категории+товары; nav «Каталог» ведёт туда; hero_image (фон-фото) из SiteSettings
- Главная (s007): hero(+фон-фото), плашки преимуществ (.benefits), категории, популярное, CTA-полоса (.cta-band)
- buybar на карточке: живой итог qty×цена через app.js (data-line-total/data-unit)
- `store/cart.py` — Cart (add/set_qty/change/remove/iter/totals)
- `store/forms.py` — OrderForm (каналы из SiteSettings)
- `store/notifications.py` — текст заказа + tg/wa ссылки + email
- `store/context_processors.py` — {{ site }}
- `store/admin.py` — админка + статистика заказов
- `store/static/store/theme.css` — дизайн-система (CSS-переменные, компоненты .btn-x/.pcard/.tabbar/...)
- `store/static/store/app.js` — JS-степпер количества (.stepper [data-dir] меняет .qty-input)
- `store/cart.py` — Cart: add/set_qty/change/change_size(размер→новый ключ, merge)/remove/iter(+prefetch sizes)
- `store/templates/store/base.html` — шапка, нижняя таб-панель, offcanvas-каталог, подвал из {{ site }}
- `store/templates/store/_product_card.html` — общая карточка товара (include)
- `store/tests.py` — 10 тестов
- `config/settings.py` — env-конфиг, прод-безопасность, email
- `.project-brain/plans/plan_002_redesign.md` — фазовый план (Фаза 3 осталась); `decisions/adr_001...`
