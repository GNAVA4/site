# Session 039 — 2026-06-14 — роль «Менеджер» (ограниченный доступ в админку)
← [session 038](./session_038_2026-06-09_admin-quickwins.md)

## Session Intent
Вход суперпользователем + возможность завести обычного staff-пользователя (менеджера), который полностью
ведёт магазин, но без критичных действий (удаление заказов и пр.). Спроектировать политику ограничений.

## Changes
| Файл | Изменение |
|------|-----------|
| `store/migrations/0017_manager_group.py` (НОВЫЙ) | data-миграция: группа «Менеджеры» с 24 правами (см. ADR 007). Идемпотентна; create_permissions() чтобы права моделей существовали к моменту привязки |
| `store/admin.py` | `OrderAdmin.has_delete_permission` и `CategoryAdmin.has_delete_permission` → только суперпользователь (defense-in-depth) |

## Политика (ADR 007)
Менеджер (is_staff + группа «Менеджеры») МОЖЕТ: товары/размеры/фото/баннеры (CRUD), категории (add/change,
без delete — каскад на товары), заказы (change/view, без add/delete — деньги+ПДн), настройки сайта (change).
НЕ МОЖЕТ: удалять заказы/категории, управлять пользователями/правами (auth не выдан → /admin/auth/ = 403).

## What works now (evidence)
- `migrate` → 0017 OK; группа «Менеджеры» = 24 права (товары/баннеры CRUD; category без delete; order только
  change/view; orderitem view; sitesettings change/view; auth — нет).
- Смоук (временный менеджер, удалён): change_order=T, delete_order=F, add_order=F, delete_category=F,
  change_product=T, delete_product=T, change_sitesettings=T, auth.add_user=F, auth.change_group=F.
  OrderAdmin/CategoryAdmin.has_delete=False. Страницы магазина 200, /admin/auth/user/ = **403**.
- `manage.py check` 0 issues; `manage.py test` **43/43 OK**.

## Заметки
- Суперпользователь уже есть: **`rus`** (из SQLite-переноса). Забыл пароль → `manage.py changepassword rus`.
  Новый суперюзер → `createsuperuser`.
- Завести менеджера: Админка → Пользователи → Добавить → is_staff (Статус персонала) + группа «Менеджеры».
- Группа создаётся миграцией → на проде появится при `migrate` автоматически.
- delete_product менеджеру разрешён осознанно: OrderItem.product=SET_NULL → история заказа (снапшот) цела.

## Session Intent check
Достигнут. Политика спроектирована и реализована (группа + защита в коде), проверена смоуком: менеджер ведёт
магазин, но не удаляет заказы/категории и не трогает пользователей.
