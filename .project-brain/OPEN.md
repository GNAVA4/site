# OPEN ITEMS — my_shop
_Updated: 2026-06-03 session 033_

## In progress
- (нет — идёт полировка по фидбэку; функционал стабилен, 13 тестов зелёные)

## TODO
- [ ] Загрузить hero_image и about_image в админке (фото строителей на главной/о магазине) `[medium]`
- [ ] Прод-подготовка `[medium]` — SQLite→Postgres, collectstatic, локальный Bootstrap (надёжность РФ),
  прод SECRET_KEY/SMTP/ALLOWED_HOSTS/CSRF_TRUSTED_ORIGINS в окружении
- [ ] Подставить реальные реквизиты в /privacy/ (наименование/ИП) `[low]`
- [ ] Убрать неиспользуемый settings.TELEGRAM_MANAGER; удалить мёртвый product_list.html; осиротевшие media/banners/ `[quick-win]`
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
