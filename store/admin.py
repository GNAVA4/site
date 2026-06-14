import csv

from django.contrib import admin
from django.db.models import Sum, Count, F, Q
from django.http import HttpResponse
from django.utils.html import format_html

from .models import (
    Category, Product, ProductSize, ProductImage, Banner,
    SiteSettings, Order, OrderItem,
)

# Брендирование админки
admin.site.site_header = 'СтройМаг — администрирование'
admin.site.site_title = 'СтройМаг'
admin.site.index_title = 'Управление магазином'


def _thumb(image, size=44):
    """Квадратная миниатюра картинки для списков админки (или «—», если фото нет)."""
    if image:
        return format_html(
            '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:6px;" />',
            image.url, size, size,
        )
    return '—'


# Позволяет добавлять размеры прямо на странице товара
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


# Доп. фото товара (галерея) прямо на странице товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_preview',)

    @admin.display(description='Превью')
    def image_preview(self, obj):
        return _thumb(obj.image)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'name', 'slug', 'icon', 'discount_percent', 'discount_target', 'views')
    list_display_links = ('name',)
    list_editable = ('icon', 'discount_percent', 'discount_target')  # Скидку на категорию правим прямо в списке
    readonly_fields = ('views',)  # Запрещаем редактировать статистику руками
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Фото')
    def image_preview(self, obj):
        return _thumb(obj.image)

    def has_delete_permission(self, request, obj=None):
        # Удаление категории каскадом удаляет её товары — только суперпользователь.
        return request.user.is_superuser


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'category', 'price_retail', 'discount_percent', 'discount_target', 'stock', 'views', 'is_active', 'is_hit')
    list_display_links = ('title',)
    list_filter = ('category', 'is_active', 'is_hit', 'discount_target')
    search_fields = ('title',)
    list_editable = ('price_retail', 'discount_percent', 'discount_target', 'stock', 'is_active', 'is_hit')
    readonly_fields = ('views',)
    inlines = [ProductSizeInline, ProductImageInline]

    @admin.display(description='Фото')
    def image_preview(self, obj):
        return _thumb(obj.image)


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'is_active')
    list_display_links = ('title',)

    @admin.display(description='Фон')
    def image_preview(self, obj):
        return _thumb(obj.image)


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Бренд", {'fields': ('shop_name', 'accent_color', 'low_stock_threshold')}),
        ("Тексты главной", {'fields': ('hero_title', 'hero_subtitle', 'hero_image')}),
        ("Страница «О магазине»", {'fields': ('about_image',)}),
        ("Контакты", {'fields': ('phone', 'email', 'telegram_username', 'whatsapp_phone', 'address', 'map_lat', 'map_lon', 'working_hours')}),
        ("Каналы оформления заказа", {
            'fields': ('enable_telegram', 'enable_whatsapp', 'enable_email', 'enable_callback', 'enable_call'),
            'description': "Отметьте, какие способы оформления показывать покупателям.",
        }),
    )

    def has_add_permission(self, request):
        # Singleton: запрещаем создавать вторую строку.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_title', 'size', 'quantity', 'price_retail', 'price_wholesale')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'customer_name', 'customer_phone', 'contact_method', 'status', 'total_retail', 'items_count', 'created_at')
    list_filter = ('status', 'contact_method', 'created_at')
    search_fields = ('customer_name', 'customer_phone', 'code')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    readonly_fields = ('code', 'total_retail', 'total_wholesale', 'created_at', 'contact_method')
    inlines = [OrderItemInline]
    actions = ['mark_processing', 'mark_done', 'mark_canceled', 'export_csv']

    def has_delete_permission(self, request, obj=None):
        # Заказы — финансовые записи + ПДн: удалять может только суперпользователь.
        return request.user.is_superuser

    # --- Массовые действия ---
    @admin.action(description='Пометить: В работе')
    def mark_processing(self, request, queryset):
        n = queryset.update(status=Order.Status.PROCESSING)
        self.message_user(request, f'Помечено «В работе»: {n}')

    @admin.action(description='Пометить: Выполнен')
    def mark_done(self, request, queryset):
        n = queryset.update(status=Order.Status.DONE)
        self.message_user(request, f'Помечено «Выполнен»: {n}')

    @admin.action(description='Пометить: Отменён')
    def mark_canceled(self, request, queryset):
        n = queryset.update(status=Order.Status.CANCELED)
        self.message_user(request, f'Помечено «Отменён»: {n}')

    @admin.action(description='Экспорт выбранных в CSV')
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="orders.csv"'
        response.write('﻿')  # BOM — чтобы Excel открыл UTF-8 с кириллицей
        writer = csv.writer(response, delimiter=';')
        writer.writerow(['ID', 'Код', 'Дата', 'Имя', 'Телефон', 'Канал', 'Статус', 'Сумма (розница)', 'Позиций'])
        for o in queryset:
            writer.writerow([
                o.id, o.code, o.created_at.strftime('%d.%m.%Y %H:%M'),
                o.customer_name, o.customer_phone,
                o.get_contact_method_display(), o.get_status_display(),
                o.total_retail, o.items_count,
            ])
        return response

    def changelist_view(self, request, extra_context=None):
        """Сводная статистика над списком — по ОТФИЛЬТРОВАННЫМ заказам (учитывает фильтры/период/поиск).
        Выручка считается без отменённых заказов."""
        response = super().changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response  # напр. редирект после массового действия — статистика не нужна

        agg = qs.aggregate(
            revenue=Sum('total_retail', filter=~Q(status=Order.Status.CANCELED)),
            orders=Count('id'),
        )
        status_labels = dict(Order.Status.choices)
        by_status = [
            {'label': status_labels.get(r['status'], r['status']), 'n': r['n']}
            for r in qs.values('status').annotate(n=Count('id')).order_by('-n')
        ]
        top_products = list(
            OrderItem.objects.filter(order__in=qs)
            .values(name=F('product_title'))
            .annotate(sold=Sum('quantity'))
            .order_by('-sold')[:5]
        )
        response.context_data['stats'] = {
            'revenue': agg['revenue'] or 0,
            'orders': agg['orders'] or 0,
            'by_status': by_status,
            'top_products': top_products,
        }
        return response
