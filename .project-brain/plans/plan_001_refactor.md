# Plan 001: Усиление магазина (рефакторинг по списку приоритетов)
_Created session 001 | Status: in-progress_

Goal: устранить критичные баги корзины, привести к деплой-готовности, убрать N+1 и противоречия UI↔логика. Опт/розница — по решению пользователя ОБЕ цены показываем намеренно (это не баг, правим только текст карточки при необходимости).

- [x] Step 1 (🔴): Рефактор корзины — структурное хранение в сессии вместо парсинга строки `ID_SIZE`. Устойчивость к удалённым/неактивным товарам (один запрос filter(pk__in)). Учёт stock при добавлении. → verify: ручной разбор + manage.py check
- [x] Step 2 (🔴): POST+CSRF для remove_from_cart / clear_cart (было изменение состояния через GET). Шаблоны → формы. → verify: check + grep отсутствия GET-ссылок
- [x] Step 3 (🔴): .env-конфиг — SECRET_KEY/DEBUG/ALLOWED_HOSTS из окружения, прод-настройки безопасности, STATIC_ROOT, лог в BASE_DIR, MEDIA_ROOT через Path. → verify: check --deploy
- [x] Step 4 (🟡): Просмотры через F() (атомарно, без гонок). → verify: code review
- [x] Step 5 (🟡): Опт/розница — снять противоречие текста (оставляем обе цены по решению юзера). → verify: визуально в шаблоне
- [x] Step 6 (🟡): select_related/prefetch_related в списках + удалить дубль URL clear_cart. → verify: check ✓ (manage.py check чист)
- [ ] Step 7 (🟡): Тесты корзины (add/remove/clear/stock/удалённый товар). → verify: manage.py test

Checkpoints: пауза после Step 6 (конец session 001) для ревью пользователя. Step 7 — отдельная сессия.
