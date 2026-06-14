# OPEN ITEMS — my_shop
_Updated: 2026-06-14 session 041_

## In progress
- (нет — идёт полировка по фидбэку; функционал стабилен, 13 тестов зелёные)

## TODO
- [ ] **Прод Партия 2 — РАЗВЕРНУТЬ** `[medium]`: артефакты ГОТОВЫ (deploy/: gunicorn.service, nginx.conf,
  backup.sh, DEPLOY.md +раздел Безопасность; ADR 006). Ждёт: заказ РФ-VPS (Ubuntu LTS) + домен (A-запись).
  От пользователя: провайдер/IP/домен; вариант A (я даю команды) или B (SSH-доступ мне). Затем DEPLOY.md + certbot.
- [ ] **Серверный харднинг при деплое** (DEPLOY §Безопасность) `[medium]`: ufw (только 22/80/443), Postgres на
  localhost, SSH по ключу (без root/паролей), fail2ban, unattended-upgrades, офсайт-копия бэкапов,
  changepassword rus, сильный пароль БД. Опц.: IP-троттлинг/капча формы заказа, jail fail2ban для /admin/.
- [ ] **РЕШЕНИЕ:** Bootstrap/FontAwesome вендорить локально vs оставить cdnjs `[low]` (cdnjs уже работает
  в РФ — это опц. усиление; вендоринг = ~5 МБ webfonts + правка url() под manifest).
- [ ] Подставить реальные реквизиты ИП в /privacy/ (юр.лицо у пользователя есть) `[low]`
- [ ] Загрузить hero_image и about_image в админке (фото на главной/о магазине) `[medium]`
- [ ] Репо публичный: дефолтный django-insecure SECRET_KEY открыт → на проде обязателен DJANGO_SECRET_KEY из env; опц. убрать хардкод-fallback `[low]`
- [ ] Опц. апгрейд поиска на pg_trgm/SearchVector (теперь возможно — Postgres и в dev; ADR 003/005) `[low]`
- [ ] Доработки админки (из аудита s038, средн./низкий): поле порядка категорий (sort); индикация/фильтр «мало осталось» в товарах (low_stock_threshold); заметка менеджера к заказу; autocomplete категории; ограничение доступа к ПДн по группам `[low]`
- [x] Прод Партия 1 (s035): SQLite→Postgres (Docker, ADR 005), WhiteNoise+gunicorn, .env.example, чистка `[done]`
- [x] поиск по товарам — реализован (s026, ADR 003); осталось (опц.) slug/SEO `[low]`

## Open bugs
- (нет открытых)

## Pending verification (user)
- [ ] НОВОЕ (s032): простые фильтры каталога/категории (без переполнения, таб-панель стабильна),
  расширенные фильтры поиска (на телефоне выезжающая панель + «Применить»), галерея фото товара.
- [x] Verified by user 2026-06-03: «визуально всё вроде норм» — поиск + поле в шапке/моб.шапка,
  скидки (товар/категория), редизайн/виджеты (до s031).

## Open questions / decisions needed
- [ ] Прод: хостинг и БД? (влияет на settings/DATABASES)
- [ ] Прод SMTP-доступы (EMAIL_HOST/USER/PASSWORD) в окружении

## Resolved (recent)
- [x] Предрелизный харднинг (s041): honeypot анти-спам формы заказа, SECRET_KEY-гард (DEBUG=False), уровень логов из env, раздел Безопасность в DEPLOY.md. check 0, 45/45 [user]
- [x] Авто-уведомление магазина о заказе (s040): email на SiteSettings.email при любом канале + ссылка на админку; не роняет оформление. check 0, 44/44 [user]
- [x] Роль «Менеджер» (s039): группа с 24 правами (миграция 0017, ADR 007) — ведёт магазин без удаления заказов/категорий и без auth; защита в коде. Суперюзер rus. check 0, 43/43 [user]
- [x] Админка «быстрые победы» (s038): превью фото, брендирование, массовые действия + CSV заказов, статистика по фильтру (без отменённых). check 0, 43/43, смоук 200 [user]
- [x] Деплой-бандл (s037): deploy/ (gunicorn.service, nginx.conf, backup.sh, DEPLOY.md) + ADR 006 топология прода [user]
- [x] Перенос данных SQLite→Postgres (s036): dumpdata/loaddata 61 объект, фикс «пустого сайта» [user]
- [x] Прод-Партия 1 (s035): PostgreSQL dev(Docker)+prod через DATABASE_URL (ADR 005), psycopg3, WhiteNoise+gunicorn, .env.example; чистка TELEGRAM_MANAGER/product_list.html; 43/43 на Postgres, check --deploy 0 issues [user]
- [x] README + git init/push на github.com/GNAVA4/site (s034); убран Claude из соавторов (amend+force-push) [user]
- [x] Фиксы фильтров поиска (s033): крестик offcanvas (data-bs-target), убран видимый {#комментарий#}, поиск без запроса = товары+фильтры [user]
- [x] Убран раздел «Скидки» /sale/ (s032): фильтр «со скидкой» переехал в общие фильтры [user]
- [x] Фикс простых фильтров (s032): убраны поля цены → нет переполнения, таб-панель не дёргается [user]
- [x] Расширенные фильтры поиска (s032): категория/цена/в наличии/скидка/хиты/сортировка; offcanvas на моб. [user]
- [x] Витрина (s031): фильтры/сортировка/пагинация (store/listing.py) на каталоге/категории/поиске [user]
- [x] Галерея фото товара (s031): ProductImage + карусель на странице товара (миграция 0016) [user]
- [x] requirements.txt (s030): прямые зависимости пинованы (Django/pillow/django-cleanup/rapidfuzz); `pip install -r requirements.txt` [user]
- [x] Косметика скидки (s029): розничный бейдж/price-old по retail_discounted — скидка-только-опт не рисует розничный бейдж [user]
- [x] Скидка на категорию (s028): Category.discount_percent/target в админке; товарная скидка важнее, не суммируется. ADR 004 [user]
- [x] Тесты в зелёное (s027): fix make_product (slug get_or_create) + float.quantize (refresh_from_db) → 21/21 OK [user]
- [x] Моб.шапка (s027): корзина убрана из шапки телефона (есть в таб-панели/бургере), на её место — поиск [user]
- [x] Поиск по товарам (s026): Python-side, кириллица+опечатки (rapidfuzz), /search/ + поле в шапке. ADR 003 [user]
- [x] ПДн: ВАРИАНТ A — храним данные, согласие + /privacy/ оставляем (s021) [user]

## Deferred (not forgotten)
- [ ] Telegram-бот вместо deep-link; отзывы (модель Review); icon-picker с превью в админке
- [ ] Записывать факт согласия в Order (поле+дата) для аудита — при необходимости
