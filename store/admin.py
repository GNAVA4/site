from django.contrib import admin
from django.db.models import Sum, Count, F

from .models import (
    Category, Product, ProductSize, ProductImage, Banner,
    SiteSettings, Order, OrderItem,
)


# Позволяет добавлять размеры прямо на странице товара
class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1


# Доп. фото товара (галерея) прямо на странице товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'discount_percent', 'discount_target', 'views')  # Видим просмотры
    list_editable = ('icon', 'discount_percent', 'discount_target')  # Скидку на категорию правим прямо в списке
    readonly_fields = ('views',)  # Запрещаем редактировать статистику руками
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price_retail', 'discount_percent', 'discount_target', 'stock', 'views', 'is_active', 'is_hit')
    list_filter = ('category', 'is_active', 'is_hit', 'discount_target')
    search_fields = ('title',)
    list_editable = ('price_retail', 'discount_percent', 'discount_target', 'stock', 'is_active', 'is_hit')
    readonly_fields = ('views',)
    inlines = [ProductSizeInline, ProductImageInline]


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')


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

    def changelist_view(self, request, extra_context=None):
        """Добавляем сводную статистику над списком заказов."""
        qs = self.get_queryset(request)
        agg = qs.aggregate(revenue=Sum('total_retail'), orders=Count('id'))
        by_status = list(qs.values('status').annotate(n=Count('id')).order_by('-n'))
        top_products = list(
            OrderItem.objects
            .values(name=F('product_title'))
            .annotate(sold=Sum('quantity'))
            .order_by('-sold')[:5]
        )
        extra_context = extra_context or {}
        extra_context['stats'] = {
            'revenue': agg['revenue'] or 0,
            'orders': agg['orders'] or 0,
            'by_status': by_status,
            'top_products': top_products,
        }
        return super().changelist_view(request, extra_context=extra_context)
