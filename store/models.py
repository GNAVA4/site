import secrets
from decimal import Decimal, ROUND_HALF_UP

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from django.db import models


# Алфавит без похожих символов (нет I, O, 0, 1) — код легко продиктовать/ввести.
_ORDER_CODE_ALPHABET = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'


def generate_order_code(length=8):
    return ''.join(secrets.choice(_ORDER_CODE_ALPHABET) for _ in range(length))


def validate_safe_link(value):
    """Разрешаем только http(s) и относительные ссылки (начинающиеся с /).
    Блокирует javascript:, data: и прочие схемы — защита от XSS через ссылку баннера."""
    if not value:
        return
    v = value.strip().lower()
    if v.startswith('/') or v.startswith('http://') or v.startswith('https://'):
        return
    raise ValidationError('Ссылка должна начинаться с «/», «http://» или «https://».')


class DiscountTarget(models.TextChoices):
    """К чему применяется скидка — общий выбор для Product и Category."""
    RETAIL = 'retail', 'Только розница'
    WHOLESALE = 'wholesale', 'Только опт'
    BOTH = 'both', 'Розница и опт'


class SiteSettings(models.Model):
    """Глобальные настройки магазина (singleton, всегда pk=1).
    Редактируются из админки — контакты, каналы заказа, тексты, акцентный цвет темы."""

    shop_name = models.CharField("Название магазина", max_length=100, default="СтройМаг")
    accent_color = models.CharField(
        "Акцентный цвет (hex)", max_length=7, default="#2c7be5",
        help_text="Главный цвет кнопок и акцентов, например #2c7be5",
    )

    # Контакты
    phone = models.CharField("Телефон", max_length=30, blank=True, help_text="Для кнопки «Позвонить» и заказа звонка")
    email = models.EmailField("Email для заказов", blank=True)
    telegram_username = models.CharField("Telegram (username без @)", max_length=50, blank=True)
    whatsapp_phone = models.CharField("WhatsApp (только цифры, напр. 79990000000)", max_length=20, blank=True)
    address = models.CharField("Адрес", max_length=255, blank=True)
    map_lat = models.CharField("Координата: широта (напр. 55.616066)", max_length=20, blank=True)
    map_lon = models.CharField("Координата: долгота (напр. 37.482762)", max_length=20, blank=True)
    working_hours = models.CharField("Часы работы", max_length=100, blank=True)

    # Тексты главной
    hero_title = models.CharField("Заголовок на главной", max_length=200, blank=True)
    hero_subtitle = models.CharField("Подзаголовок на главной", max_length=300, blank=True)
    hero_image = models.ImageField("Фон-фото на главной (строители и т.п.)", upload_to='site/', blank=True, null=True)
    about_image = models.ImageField("Фон-фото на странице «О магазине»", upload_to='site/', blank=True, null=True)
    low_stock_threshold = models.PositiveIntegerField("Порог «мало осталось»", default=5,
                                                      help_text="Если остаток ≤ этого числа — бейдж «Мало осталось»")

    # Какие каналы оформления показывать покупателю
    enable_telegram = models.BooleanField("Канал: Telegram", default=True)
    enable_whatsapp = models.BooleanField("Канал: WhatsApp", default=False)
    enable_email = models.BooleanField("Канал: Email", default=False)
    enable_callback = models.BooleanField("Канал: Позвоните мне", default=True)
    enable_call = models.BooleanField("Канал: Позвоню сам", default=True)

    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1  # всегда одна строка
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Category(models.Model):
    ICON_CHOICES = [
        ('fa-box', '📦 Коробка (по умолчанию)'),
        # Текстиль / спальное / одежда
        ('fa-bed', '🛏 Матрас / кровать'),
        ('fa-mattress-pillow', '🛏 Матрас с подушкой'),
        ('fa-couch', '🛋 Мебель / диван'),
        ('fa-chair', '🪑 Мебель / стул'),
        ('fa-shirt', '👕 Одежда'),
        ('fa-helmet-safety', '⛑ Спецодежда / каска'),
        ('fa-socks', '🧦 Текстиль / носки'),
        ('fa-shoe-prints', '👟 Обувь'),
        ('fa-baby', '👶 Детское'),
        # Кухня / посуда
        ('fa-utensils', '🍴 Посуда / столовые приборы'),
        ('fa-kitchen-set', '🍳 Кухня / кухонная утварь'),
        ('fa-mug-hot', '☕ Кружки / посуда'),
        ('fa-bowl-food', '🥣 Посуда / миски'),
        # Сад / огород
        ('fa-seedling', '🌱 Сад / рассада'),
        ('fa-leaf', '🍃 Сад / растения'),
        ('fa-tree', '🌳 Сад / деревья'),
        ('fa-shovel', '🪏 Садовый инструмент'),
        # Инструмент / стройка / крепёж
        ('fa-toolbox', '🧰 Инструменты'),
        ('fa-screwdriver-wrench', '🔧 Инструмент / крепёж'),
        ('fa-hammer', '🔨 Молоток / инструмент'),
        ('fa-wrench', '🔧 Ключи / сантех.инструмент'),
        ('fa-trowel-bricks', '🧱 Стройматериалы'),
        ('fa-ruler-combined', '📐 Замеры / размеры'),
        # Отделка / краски
        ('fa-paint-roller', '🎨 Отделка / малярка'),
        ('fa-brush', '🖌 Кисти'),
        ('fa-fill-drip', '🪣 Краски / ЛКМ'),
        # Сантехника / электрика / свет
        ('fa-faucet', '🚰 Сантехника'),
        ('fa-shower', '🚿 Душ / ванная'),
        ('fa-toilet', '🚽 Сантехника / унитазы'),
        ('fa-bolt', '⚡ Электрика'),
        ('fa-plug', '🔌 Электрика / розетки'),
        ('fa-lightbulb', '💡 Свет / лампы'),
        # Двери / замки / хозтовары / климат
        ('fa-door-open', '🚪 Двери'),
        ('fa-key', '🔑 Замки / фурнитура'),
        ('fa-broom', '🧹 Хозтовары / уборка'),
        ('fa-bucket', '🪣 Хозтовары / вёдра'),
        ('fa-spray-can', '🧴 Бытовая химия'),
        ('fa-fan', '🌀 Вентиляция'),
        ('fa-snowflake', '❄ Климат / охлаждение'),
        ('fa-temperature-half', '🌡 Отопление'),
        ('fa-car', '🚗 Авто / гараж'),
        # Прочее / витрина
        ('fa-truck', '🚚 Доставка'),
        ('fa-warehouse', '🏬 Склад'),
        ('fa-tags', '🏷 Распродажа'),
        ('fa-fire', '🔥 Хиты'),
    ]

    name = models.CharField("Название категории", max_length=100)
    slug = models.SlugField("Ссылка (slug)", max_length=100, unique=True)
    image = models.ImageField("Фото категории", upload_to='categories/', blank=True, null=True)
    icon = models.CharField("Иконка", max_length=40, choices=ICON_CHOICES, default='fa-box',
                            help_text="Показывается в плитках каталога")

    # Скидка на всю категорию. Действует только на товары БЕЗ собственной скидки — не суммируется.
    discount_percent = models.PositiveSmallIntegerField(
        "Скидка на категорию, %", default=0, validators=[MaxValueValidator(95)],
        help_text="0 = без скидки. Применяется к товарам категории, у которых НЕТ своей скидки (не суммируется).",
    )
    discount_target = models.CharField(
        "Скидка категории применяется к", max_length=10,
        choices=DiscountTarget.choices, default=DiscountTarget.RETAIL,
    )

    # Аналитика
    views = models.PositiveIntegerField("Просмотров", default=0)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    title = models.CharField("Название товара", max_length=200)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Фото товара", upload_to='products/')

    price_retail = models.DecimalField("Цена розничная", max_digits=10, decimal_places=0)
    price_wholesale = models.DecimalField("Цена оптовая", max_digits=10, decimal_places=0)

    discount_percent = models.PositiveSmallIntegerField(
        "Скидка, %", default=0, validators=[MaxValueValidator(95)],
        help_text="0 = без скидки. Напр. 20 = −20%.",
    )
    discount_target = models.CharField(
        "Скидка применяется к", max_length=10,
        choices=DiscountTarget.choices, default=DiscountTarget.RETAIL,
    )

    stock = models.PositiveIntegerField("Остаток на складе", default=10)
    is_active = models.BooleanField("Показывать на сайте?", default=True)
    is_hit = models.BooleanField("Хит продаж (бейдж)", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Аналитика
    views = models.PositiveIntegerField("Просмотров товара", default=0)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']  # Свежие сверху

    def __str__(self):
        return self.title

    @property
    def effective_discount_percent(self):
        """Действующая скидка: СВОЯ скидка товара важнее скидки категории — они НЕ суммируются.
        Если у товара своя скидка (>0) — берём её; иначе скидку категории; иначе 0."""
        if self.discount_percent:
            return self.discount_percent
        if self.category_id and self.category.discount_percent:
            return self.category.discount_percent
        return 0

    @property
    def effective_discount_target(self):
        """К чему применяется действующая скидка (товара или, при её отсутствии, категории)."""
        if self.discount_percent:
            return self.discount_target
        if self.category_id and self.category.discount_percent:
            return self.category.discount_target
        return self.discount_target

    @property
    def has_discount(self):
        return self.effective_discount_percent > 0

    def _discounted(self, base):
        value = base * (100 - self.effective_discount_percent) / 100
        return value.quantize(Decimal('1'), rounding=ROUND_HALF_UP)

    @property
    def retail_discounted(self):
        return self.has_discount and self.effective_discount_target in ('retail', 'both')

    @property
    def wholesale_discounted(self):
        return self.has_discount and self.effective_discount_target in ('wholesale', 'both')

    @property
    def current_retail(self):
        """Фактическая розничная цена (с учётом скидки товара/категории), округлённая до рубля."""
        return self._discounted(self.price_retail) if self.retail_discounted else self.price_retail

    @property
    def current_wholesale(self):
        """Фактическая оптовая цена (с учётом скидки товара/категории), округлённая до рубля."""
        return self._discounted(self.price_wholesale) if self.wholesale_discounted else self.price_wholesale

    @property
    def gallery(self):
        """Изображения для слайдера на странице товара: обложка (product.image) + доп. фото по порядку."""
        imgs = [self.image] if self.image else []
        imgs += [pi.image for pi in self.images.all()]
        return imgs


# Новая модель: Размеры
class ProductSize(models.Model):
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    size_value = models.CharField("Значение (40, XL, 200x300)", max_length=50)

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.size_value


class ProductImage(models.Model):
    """Дополнительные фото товара (галерея). Обложка остаётся в Product.image."""
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField("Доп. фото", upload_to='products/')
    sort = models.PositiveIntegerField("Порядок", default=0, help_text="Чем меньше — тем раньше")

    class Meta:
        verbose_name = "Фото товара (галерея)"
        verbose_name_plural = "Фото товара (галерея)"
        ordering = ['sort', 'id']

    def __str__(self):
        return f"Фото №{self.pk} для товара {self.product_id}"


# Новая модель: Баннеры на главной
class Banner(models.Model):
    title = models.CharField("Заголовок", max_length=100)
    text = models.TextField("Текст акции")
    image = models.ImageField("Фон баннера", upload_to='promo/', blank=True, null=True)
    link = models.CharField("Ссылка (например /category/matrasy/)", max_length=200, blank=True,
                            validators=[validate_safe_link])
    is_active = models.BooleanField("Активен?", default=True)

    class Meta:
        verbose_name = "Рекламный баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return self.title


class Order(models.Model):
    class ContactMethod(models.TextChoices):
        TELEGRAM = 'telegram', 'Telegram'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        EMAIL = 'email', 'Email'
        CALLBACK = 'callback', 'Позвоните мне'
        CALL = 'call', 'Позвоню сам'

    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        PROCESSING = 'processing', 'В работе'
        DONE = 'done', 'Выполнен'
        CANCELED = 'canceled', 'Отменён'

    code = models.CharField("Код заказа", max_length=12, blank=True, db_index=True,
                            help_text="Код для проверки заказа покупателем (генерируется автоматически)")
    customer_name = models.CharField("Имя покупателя", max_length=150)
    customer_phone = models.CharField("Телефон", max_length=30, blank=True)
    contact_method = models.CharField(
        "Способ связи", max_length=20, choices=ContactMethod.choices, default=ContactMethod.TELEGRAM,
    )
    comment = models.TextField("Комментарий", blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)

    # Снапшот итогов на момент заказа (decimal_places=0 — как у товаров)
    total_retail = models.DecimalField("Сумма (розница)", max_digits=12, decimal_places=0, default=0)
    total_wholesale = models.DecimalField("Сумма (опт)", max_digits=12, decimal_places=0, default=0)

    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_order_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заказ #{self.pk} — {self.customer_name}"

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # Товар может быть удалён позже — заказ сохраняет снапшот, ссылка обнуляется.
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.SET_NULL)

    product_title = models.CharField("Товар (снапшот)", max_length=200)
    size = models.CharField("Размер", max_length=50, default="Стандарт")
    quantity = models.PositiveIntegerField("Количество", default=1)
    price_retail = models.DecimalField("Цена розн. (снапшот)", max_digits=10, decimal_places=0)
    price_wholesale = models.DecimalField("Цена опт. (снапшот)", max_digits=10, decimal_places=0)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product_title} ({self.size}) ×{self.quantity}"

    @property
    def sum_retail(self):
        return self.price_retail * self.quantity

    @property
    def sum_wholesale(self):
        return self.price_wholesale * self.quantity