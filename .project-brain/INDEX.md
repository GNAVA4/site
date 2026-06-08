# MEMORY INDEX — my_shop
_Updated: 2026-06-08 session 035_

## By topic
| Topic | Files |
|-------|-------|
| корзина | session_001, session_003, insight_2026-05-31_cart-string-key, plan_001 |
| заказы/чекаут/статистика | session_002, session_003, adr_001, plan_002 |
| скидки/цены | session_019 (Product.discount_percent/current_retail), session_028 (скидка категории, effective_discount_*, adr_004) |
| корзина-виджет/AJAX/toast | session_016, session_019 |
| каналы заказа (tg/wa/email/звонок) | session_003, store/notifications.py, store/forms.py |
| настройки сайта (SiteSettings) | session_002, session_003, adr_001 |
| дизайн/редизайн | session_005, plan_002, store/static/store/theme.css, design-skills (frontend-design/theme-factory) |
| тесты | session_003, store/tests.py |
| деплой/безопасность | session_001, session_003, CONTEXT |
| git/README/публикация | session_034, README.md, .gitignore (remote github.com/GNAVA4/site) |
| прод-подготовка/БД/деплой | session_035, adr_005, docker-compose.yml, .env.example, settings.py (DATABASE_URL/WhiteNoise/gunicorn) |
| архитектура | architecture.md |
| поиск товаров | session_026, store/search.py, adr_003, insight_2026-06-02_sqlite-cyrillic-icase |
| витрина/фильтры/пагинация | session_031+032, store/listing.py, _browse_controls (простые), _pager |
| расширенные фильтры поиска | session_032, _search_filters.html (offcanvas), listing.browse(relevance_pks) |
| галерея фото товара | session_031, ProductImage, product_detail.html (carousel) |
| (удалено) страница «Скидки» /sale/ | была session_031, убрана session_032 |

## Sessions
| # | Date | Topic | Touched |
|---|------|-------|---------|
| 001 | 2026-05-31 | анализ + рефактор корзины/безопасности | cart, views, settings, urls, templates |
| 002 | 2026-05-31 | Фаза 1: backend заказов | models, admin, миграция 0003, admin template |
| 003 | 2026-05-31 | Фаза 2: оформление заказа + корзина-степпер | forms, notifications, context_processors, views, urls, templates, tests, settings |
| 004 | 2026-05-31 | правки каналов (email-mailto, переименование, телефон без +7) | models, forms, notifications, views, templates, tests, миграция 0004 |
| 005 | 2026-05-31 | Фаза 3: mobile-first редизайн (строгая тема) | theme.css (НОВЫЙ), base + все шаблоны, _product_card |
| 006 | 2026-05-31 | UX-фидбэк: размеры на карточке/в корзине, JS-степперы, фон/категории, моб.карточка + CDN-фикс | theme.css, app.js (НОВЫЙ), cart.py, views, шаблоны, tests |
| 007 | 2026-05-31 | страница /catalog/, живой итог в buybar, фикс моб.корзины, плашки/CTA/hero_image | catalog.html (НОВ), views, urls, models(0005), base, index, app.js, theme.css |
| 008 | 2026-05-31 | фикс баннеров (img), баннер категории, фон менее белый, размер↔кол-во | index, category_detail, _product_card, theme.css |
| 009 | 2026-05-31 | НАСТОЯЩИЙ фикс баннеров: ad-blocker резал «banner» → папка promo, переименование (миграция 0006) | models, index, theme.css, медиа |
| 010 | 2026-05-31 | фикс отступа размер↔кол-во (gap внутри form); Яндекс.Карта в контактах из site.address | theme.css, contacts.html |
| 011 | 2026-05-31 | точная метка на карте по координатам + кнопка «Проложить маршрут» (миграция 0007) | models, admin, contacts.html |
| 012 | 2026-05-31 | страница «О магазине» + иконки категорий (выбор в админке, миграция 0008) | about.html (НОВ), views, urls, models, admin, base, index, catalog, theme.css |
| 013 | 2026-05-31 | палитра сине-стальная+тёплый акцент; бейджи (is_hit/low_stock); FAQ; похожие товары; about_image (миграция 0009) | models, admin, views, theme.css, _product_card, product_detail, index, about |
| 014 | 2026-05-31 | мобильное меню-гамбургер в шапке (О магазине доступно на телефоне) | base.html |
| 015 | 2026-05-31 | расширен набор иконок категорий (~45, миграция 0010) + иконки в десктопном меню категорий | models, base.html |
| 016 | 2026-05-31 | AJAX-корзина + toast (без прыжка наверх); фикс переполнения моб.корзины; стабилизация нижней панели | app.js, theme.css, base.html, _product_card, product_detail, views |
| 017 | 2026-05-31 | toast наверх (моб.); согласие на ПДн + /privacy/; фиксы безопасности (Banner.link, stretched-link, CSRF_TRUSTED_ORIGINS) | forms, views, urls, models, settings, templates, tests, миграция 0011 |
| 018 | 2026-05-31 | фикс горизонт. вылета на узких экранах (min-width:0 + overflow-x:clip) + safe-area нижней панели | theme.css |
| 019 | 2026-05-31 | скидки (discount_percent, current_retail, зачёркнутая цена, миграция 0012); плавающий виджет корзины (моб.); статичная кнопка вместо buybar | models, admin, cart, views, context_processors, app.js, theme.css, templates, tests |
| 020 | 2026-05-31 | скидка на опт (discount_target, миграция 0013); анимация выезда виджета справа; виджет на ПК | models, admin, cart, views, theme.css, app.js, base, templates |
| 021 | 2026-05-31 | фикс: непрозрачная нижняя панель (карта-iframe не перехватывает тапы); ПДн = вариант A | theme.css |
| 022 | 2026-05-31 | ПРАВИЛЬНЫЙ фикс: .map-frame pointer-events:none + ссылка-оверлей; панель вернули с blur | theme.css, contacts.html |
| 023 | 2026-05-31 | счётчик корзины белым (без пилюли); карточка: степпер+кнопка в один ряд, на моб. иконка | base.html, theme.css, _product_card |
| 024 | 2026-05-31 | гостевой трекинг заказа по коду (/order/track/, Order.code, миграция 0014, ADR 002) + автоподстановка (localStorage) | models, admin, views, urls, notifications, app.js, templates, tests |
| 025 | 2026-05-31 | «Проверить заказ» в верхнее меню (ПК) и мобильное меню | base.html |
| 026 | 2026-06-02 | поиск по товарам (Python-side, rapidfuzz, кириллица+опечатки) + /search/ + поле в шапке | search.py (НОВ), views, urls, search.html (НОВ), base, theme.css, tests; +rapidfuzz |
| 027 | 2026-06-02 | тесты в зелёное (fix make_product slug + float.quantize) 21/21; моб.шапка: поиск вместо корзины (корзина→таб-панель/бургер) | tests.py, base.html |
| 028 | 2026-06-03 | скидка на категорию (Category.discount_*, миграция 0015) + Product.effective_discount_* (товар важнее, не суммируется), ADR 004 | models, admin, _product_card, product_detail, tests, 0015 |
| 029 | 2026-06-03 | косметика скидки: розничный бейдж/price-old по retail_discounted (скидка-только-опт не рисует розничный бейдж) | _product_card, product_detail, tests |
| 030 | 2026-06-03 | requirements.txt — зафиксированы прямые зависимости (Django/pillow/django-cleanup/rapidfuzz) | requirements.txt (НОВ) |
| 031 | 2026-06-03 | витрина (фильтры/сортировка/пагинация, store/listing.py) + страница «Скидки» /sale/ + галерея фото товара (ProductImage, миграция 0016) | listing.py (НОВ), views, urls, models, admin, шаблоны, theme.css, tests, 0016 |
| 032 | 2026-06-03 | убран раздел «Скидки» (/sale/); простые фильтры каталога/категории (фикс переполнения); расширенные фильтры поиска (offcanvas на моб. + «Применить») | listing.py, views, urls, base, _browse_controls, _search_filters (НОВ), search.html, theme.css, tests; sale.html удалён |
| 033 | 2026-06-03 | фиксы фильтров поиска: крестик offcanvas (data-bs-target), убран видимый {#многострочный комментарий#}, поиск без запроса = все товары + фильтры (режимы browse/results/empty) | _search_filters, views.search, search.html, tests |
| 034 | 2026-06-08 | README (установка/запуск) + .gitignore; git init + push на github.com/GNAVA4/site (main, 2db2b1d, без Claude в соавторах); проверка секретов (db/media/venv/логи не в репо) | README.md (НОВ), .gitignore (НОВ), git |
| 035 | 2026-06-08 | Прод-Партия 1: SQLite→PostgreSQL (dev Docker:5433 + прод DATABASE_URL, ADR 005, psycopg3); WhiteNoise+STORAGES+gunicorn; .env.example; чистка (TELEGRAM_MANAGER, product_list.html). 43/43 на Postgres, check --deploy 0 issues | docker-compose.yml (НОВ), settings.py, requirements.txt, .env.example (НОВ), README.md, adr_005 |

## Decisions (ADRs)
| # | Title | Status |
|---|-------|--------|
| 001 | Заказы в БД (Order/OrderItem) + SiteSettings | active |
| 002 | Гостевой трекинг заказа по коду (без аккаунтов) | active |
| 003 | Поиск на стороне Python (не SQL), rapidfuzz-Левенштейн | active |
| 004 | Скидка на категорию + приоритет товарной скидки (без суммирования) | active |
| 005 | PostgreSQL и в dev (Docker), и на проде — паритет сред | active |

## Plans
| # | Title | Status |
|---|-------|--------|
| 001 | Рефакторинг по приоритетам | Steps 1-6 done; Step 7 (тесты) сделан в s003 |
| 002 | Переделка архитектуры/дизайна (3 фазы) | Фазы 1-2 done; Фаза 3 (редизайн) pending |

## Open bugs index
| Bug | Severity | Status |
|-----|----------|--------|
| test_discount_price_and_cart_sum: slug-коллизия + float.quantize | low | fixed s027 (get_or_create + refresh_from_db) |

## Insights
| File | Тема |
|------|------|
| insight_2026-05-31_cart-string-key | нельзя хранить состояние в склеенном ключе |
| insight_2026-05-31_cdn-jsdelivr-ru-block | jsdelivr/Google Fonts режутся в РФ → стили не применяются; брать cdnjs |
| insight_2026-05-31_adblock-banner-path | ad-blocker режет пути/классы со словом «banner» → нейтральные имена (promo) |
| insight_2026-06-02_sqlite-cyrillic-icase | SQLite icontains/lower() не для кириллицы → регистр сворачивать в Python |
