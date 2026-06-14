from django.db import migrations

MANAGER_GROUP = 'Менеджеры'

# Права менеджера: (app_label, model, [действия]).
# Полное управление магазином, КРОМЕ критичного:
#   - заказы: change/view (без add/delete — финансовые записи + ПДн)
#   - категории: add/change/view (без delete — каскад сносит товары)
#   - пользователи/группы (auth): НЕ выдаём вовсе (иначе менеджер выдаст себе суперправа)
MANAGER_PERMS = [
    ('store', 'product',      ['add', 'change', 'delete', 'view']),
    ('store', 'productsize',  ['add', 'change', 'delete', 'view']),
    ('store', 'productimage', ['add', 'change', 'delete', 'view']),
    ('store', 'category',     ['add', 'change', 'view']),
    ('store', 'banner',       ['add', 'change', 'delete', 'view']),
    ('store', 'order',        ['change', 'view']),
    ('store', 'orderitem',    ['view']),
    ('store', 'sitesettings', ['change', 'view']),
]


def create_manager_group(apps, schema_editor):
    # Права моделей обычно создаются в post_migrate (в конце migrate). Создаём их сейчас,
    # чтобы они существовали к моменту привязки к группе.
    from django.contrib.auth.management import create_permissions
    from django.apps import apps as global_apps
    for app_config in global_apps.get_app_configs():
        if app_config.models_module is not None:
            create_permissions(app_config, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    group, _ = Group.objects.get_or_create(name=MANAGER_GROUP)
    perms = []
    for app_label, model, actions in MANAGER_PERMS:
        for action in actions:
            perm = Permission.objects.filter(
                codename=f'{action}_{model}', content_type__app_label=app_label,
            ).first()
            if perm:
                perms.append(perm)
    group.permissions.set(perms)


def remove_manager_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name=MANAGER_GROUP).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_productimage'),
        ('auth', '__first__'),
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_manager_group, remove_manager_group),
    ]
