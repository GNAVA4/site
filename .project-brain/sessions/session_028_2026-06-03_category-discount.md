# Session 028 — 2026-06-03 — скидка на категорию + приоритет товарной скидки (без суммирования)
← [session 027](./session_027_2026-06-02_tests-green-mobile-header.md)

## Session Intent
В админке — возможность включить скидку на всю категорию и на отдельные товары. Товары со СВОЕЙ
скидкой не суммируются с категорийной.

## Decision → ADR 004
Приоритет: **скидка товара важнее** (выбор user). Категорийная действует только на товары БЕЗ своей.
Не суммируются. (Альтернативы: max / категория важнее — отклонены.)

## Changes (with provenance)
| Изменение | Source |
|-----------|--------|
| `DiscountTarget` вынесен на уровень модуля (общий для Product и Category) | [refactor] |
| `Category.discount_percent` (0–95) + `Category.discount_target` (розница/опт/обе); миграция 0015 | [user] |
| `Product.effective_discount_percent` / `effective_discount_target`: своя >0 → она; иначе категории; иначе 0 | [user, ADR 004] |
| `has_discount`/`_discounted`/`retail_discounted`/`wholesale_discounted`/`current_*` переведены на effective | [inferred] |
| `CategoryAdmin`: discount_percent + discount_target в list_display и list_editable (правка в списке) | [user] |
| Шаблоны: бейдж «−N%» → `effective_discount_percent` (_product_card, product_detail) | [inferred] |

## Важно
- Скидка на ОТДЕЛЬНЫЕ товары уже была (`Product.discount_percent`/`discount_target`, list_editable) —
  это закрывает «для определённых товаров». Сейчас добавлена только категорийная.
- `current_retail`/`current_wholesale` теперь учитывают эффективную скидку → корзина, оформление и
  снапшот OrderItem подхватывают категорийную скидку автоматически, без двойного применения.
- Снапшот в заказе по-прежнему фиксирует фактически списанную цену на момент заказа.

## What works now (evidence)
- `makemigrations` → 0015 (только Category; Product-поле не изменилось при выносе DiscountTarget).
- `migrate` OK; `manage.py check` → no issues.
- `manage.py test` → **26/26 OK** (+5 CategoryDiscountTests): полная цена; категория применяется к товару
  без своей; своя 10% важнее категорийной 50% (current_retail=900, не 500/400); таргет только-опт
  (розница не тронута, опт −10%); категорийная скидка попадает в сумму корзины (800×2=1600).

## Files changed
- `store/models.py` — DiscountTarget на модуль; Category +2 поля; Product +effective_* и рефактор скидочных свойств.
- `store/admin.py` — CategoryAdmin: скидка в списке.
- `store/templates/store/_product_card.html`, `product_detail.html` — бейдж −% через effective.
- `store/tests.py` — +CategoryDiscountTests (5), импорт DiscountTarget.
- `store/migrations/0015_category_discount_percent_category_discount_target.py` — НОВАЯ.

## Low-pri (занесено в OPEN)
- Косметика: розничный price-old/бейдж показываются при `has_discount`; если скидка только на ОПТ,
  розничный price-old покажет ту же цену (пред-существующий мелкий баг, теперь достижим и через категорию).
  Чисто отображение; цены (current_*) считаются верно. Фикс — гейтить розничный price-old по retail_discounted.

## Session Intent check
Достигнут. Скидка на категорию в админке; товарная важнее и не суммируется; цены/корзина/заказ корректны; 26/26 тестов.
