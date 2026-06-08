# Session 029 — 2026-06-03 — косметика скидки: розничный бейдж/price-old по retail_discounted
← [session 028](./session_028_2026-06-03_category-discount.md)

## Session Intent
Закрыть low-pri из s028: при скидке ТОЛЬКО на опт у розничной цены показывались зачёркнутая та же
цена и бейдж «−N%». Гейтить розничный UI по `retail_discounted`, а не `has_discount`.

## Changes
| Изменение | Source |
|-----------|--------|
| `_product_card.html`: бейдж «−N%» (оверлей) и розничный `price-old` → `{% if product.retail_discounted %}` | [user] |
| `product_detail.html`: блок розничной цены (price-old + бейдж) → `{% if product.retail_discounted %}` | [user] |

Опт-блок уже корректно гейтился по `wholesale_discounted` — не трогал. Общий случай (скидка на
розницу/обе) рендерится как раньше; меняется только поведение скидки «только опт».

## What works now (evidence)
- `manage.py check` → no issues.
- `manage.py test` → **27/27 OK** (+1 рендер-тест `test_wholesale_only_discount_hides_retail_badge`:
  скидка-только-опт → `badge-disc` в HTML нет; переключение категории на retail → бейдж появляется).

## Files changed
- `store/templates/store/_product_card.html`, `store/templates/store/product_detail.html`, `store/tests.py`.

## Session Intent check
Достигнут. Розничный UI скидки показывается только когда дисконтируется розница; цены и так считались верно.
