import logging
import secrets
import urllib.parse

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import OrderForm
from .models import Product, Category, Banner, Order, OrderItem, SiteSettings
from .search import search_products
from . import notifications, listing

logger = logging.getLogger(__name__)


def enabled_methods(site):
    """Список включённых в админке каналов: [(value, label), ...]."""
    flags = [
        ('telegram', site.enable_telegram),
        ('whatsapp', site.enable_whatsapp),
        ('email', site.enable_email),
        ('callback', site.enable_callback),
        ('call', site.enable_call),
    ]
    labels = dict(Order.ContactMethod.choices)
    return [(value, labels[value]) for value, on in flags if on]


def get_common_context():
    return {'categories': Category.objects.all()}


FAQ = [
    ("Как сделать заказ?",
     "Выберите товар в каталоге, укажите размер и количество, добавьте в корзину и нажмите «Оформить заказ». "
     "Затем выберите удобный способ связи — менеджер подтвердит заказ."),
    ("Вы работаете оптом?",
     "Да. У каждого товара указана и розничная, и оптовая цена. Точные условия опта уточняйте у менеджера."),
    ("Как получить товар?",
     "Основной способ — самовывоз со склада. Адрес и часы работы указаны на странице «Контакты»."),
    ("Какие есть способы связи?",
     "Telegram, WhatsApp, e-mail, заявка на обратный звонок или звонок нам напрямую — выбираете при оформлении."),
    ("Можно ли заказать большой объём под бригаду?",
     "Да, под крупные заказы подберём ассортимент и рассчитаем оптовую цену — напишите или позвоните менеджеру."),
]


def home(request):
    banners = Banner.objects.filter(is_active=True)
    # Популярные товары (сортируем по просмотрам, берем топ-8)
    popular_products = (
        Product.objects.filter(is_active=True)
        .select_related('category')
        .prefetch_related('sizes')
        .order_by('-views')[:8]
    )

    context = {
        **get_common_context(),
        'banners': banners,
        'popular_products': popular_products,
        'faq': FAQ,
    }
    return render(request, 'store/index.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    # АНАЛИТИКА: +1 просмотр категории. F() — атомарно, без гонок и без
    # перезаписи всей строки (старый код терял инкременты при параллельных GET).
    Category.objects.filter(pk=category.pk).update(views=F('views') + 1)

    products = (
        Product.objects.filter(category=category, is_active=True)
        .select_related('category')
        .prefetch_related('sizes')
    )

    context = {
        **get_common_context(),
        'category': category,
        **listing.browse(products, request, hide_category=True),
    }
    return render(request, 'store/category_detail.html', context)


def product_detail(request, pk):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('sizes'),
        pk=pk,
        is_active=True,
    )

    # АНАЛИТИКА: +1 просмотр товара (атомарно через F()).
    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)

    similar = (
        Product.objects.filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)
        .select_related('category')
        .prefetch_related('sizes')[:4]
    )

    context = {
        **get_common_context(),
        'product': product,
        'similar': similar,
    }
    return render(request, 'store/product_detail.html', context)


def catalog(request):
    """Страница всего каталога: категории + витрина товаров (фильтры/сортировка/пагинация)."""
    products = (
        Product.objects.filter(is_active=True)
        .select_related('category')
        .prefetch_related('sizes')
    )
    context = {
        **get_common_context(),
        **listing.browse(products, request),
    }
    return render(request, 'store/catalog.html', context)


def about(request):
    return render(request, 'store/about.html', get_common_context())


def search(request):
    """Поиск по товарам (?q=). Логика — в store/search.py (Python-side: кириллица + опечатки)."""
    query = (request.GET.get('q') or '').strip()
    base = (Product.objects.filter(is_active=True)
            .select_related('category').prefetch_related('sizes'))

    # Без запроса — показываем все товары с фильтрами (страница-«фильтруемый каталог»).
    if not query:
        context = {
            **get_common_context(),
            'query': query, 'mode': 'browse', 'suggestions': [],
            **listing.browse(base, request),
        }
        return render(request, 'store/search.html', context)

    results, suggestions = search_products(query)
    if results:
        ranked_pks = [p.pk for p in results]
        context = {
            **get_common_context(),
            'query': query, 'mode': 'results', 'suggestions': [],
            **listing.browse(base.filter(pk__in=ranked_pks), request, relevance_pks=ranked_pks),
        }
    else:
        context = {
            **get_common_context(),
            'query': query, 'mode': 'empty', 'suggestions': suggestions,
            'products': [], 'page_obj': None,
        }
    return render(request, 'store/search.html', context)


def track_order(request):
    """Проверка заказа по номеру + коду (без аккаунтов/паролей)."""
    order = None
    error = None
    number = (request.POST.get('number') or request.GET.get('number') or '').strip()
    code = (request.POST.get('code') or request.GET.get('code') or '').strip().upper()

    if number and code:
        try:
            candidate = Order.objects.prefetch_related('items').get(pk=int(number))
        except (Order.DoesNotExist, ValueError, OverflowError):
            candidate = None
        # constant-time сравнение кода — чтобы нельзя было подобрать по таймингу
        if candidate and candidate.code and secrets.compare_digest(candidate.code, code):
            order = candidate
        else:
            error = 'Заказ не найден. Проверьте номер и код.'

    context = {
        **get_common_context(),
        'order': order, 'error': error, 'number': number, 'code': code,
    }
    return render(request, 'store/order_track.html', context)


def privacy(request):
    return render(request, 'store/privacy.html', get_common_context())


def contacts(request):
    return render(request, 'store/contacts.html', get_common_context())


# --- КОРЗИНА ---

@require_POST
def add_to_cart(request, product_id):
    size = request.POST.get('size', 'Стандарт')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    if quantity < 1:
        quantity = 1

    product = get_object_or_404(Product, pk=product_id, is_active=True)

    cart = Cart(request)
    set_qty, capped = cart.add(product, size, quantity)

    if set_qty == 0:
        ok, text = False, f'«{product.title}» нет в наличии.'
    elif capped:
        ok, text = True, f'Добавлено: {product.title} ({size}) — {set_qty} шт. (больше нет на складе).'
    else:
        ok, text = True, f'Добавлено: {product.title} ({size}) — {quantity} шт.'

    # AJAX (с карточки/детальной) — отвечаем JSON, без перезагрузки страницы.
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        total_retail, _ = cart.totals()
        return JsonResponse({
            'ok': ok, 'message': text,
            'cart_count': len(cart), 'cart_total': int(total_retail),
        })

    # Обычная отправка (без JS) — сообщение + возврат назад.
    (messages.success if ok else messages.warning)(request, text)
    return redirect(_safe_back(request))


def cart_detail(request):
    cart = Cart(request)
    cart_items = list(cart)  # один запрос к БД, см. Cart.__iter__

    total_retail = sum((i['sum_retail'] for i in cart_items), start=0)
    total_wholesale = sum((i['sum_wholesale'] for i in cart_items), start=0)

    context = {
        **get_common_context(),
        'cart_items': cart_items,
        'total_retail': total_retail,
        'total_wholesale': total_wholesale,
    }
    return render(request, 'store/cart.html', context)


@require_POST
def update_cart(request, item_key):
    """Изменение позиции корзины (только POST):
    action=inc|dec — количество; size=<значение> — смена размера."""
    cart = Cart(request)
    action = request.POST.get('action')
    new_size = request.POST.get('size')
    if action == 'inc':
        cart.change(item_key, 1)
    elif action == 'dec':
        cart.change(item_key, -1)
    elif new_size is not None:
        cart.change_size(item_key, new_size)
    return redirect('cart_detail')


@require_POST
def remove_from_cart(request, item_key):
    """Удаление одной позиции из корзины (только POST)."""
    cart = Cart(request)
    if cart.remove(item_key):
        messages.success(request, 'Товар удалён из корзины')
    return redirect('cart_detail')


@require_POST
def clear_cart(request):
    Cart(request).clear()
    return redirect('cart_detail')


def checkout(request):
    cart = Cart(request)
    cart_items = list(cart)
    if not cart_items:
        messages.info(request, 'Корзина пуста — добавьте товары перед оформлением.')
        return redirect('cart_detail')

    site = SiteSettings.load()
    methods = enabled_methods(site)
    allowed = [m[0] for m in methods]

    total_retail = sum((i['sum_retail'] for i in cart_items), start=0)
    total_wholesale = sum((i['sum_wholesale'] for i in cart_items), start=0)

    if request.method == 'POST':
        form = OrderForm(request.POST, allowed_methods=allowed)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)
                order.total_retail = total_retail
                order.total_wholesale = total_wholesale
                order.save()
                OrderItem.objects.bulk_create([
                    OrderItem(
                        order=order,
                        product=item['product'],
                        product_title=item['product'].title,
                        size=item['size'],
                        quantity=item['qty'],
                        price_retail=item['product'].current_retail,
                        price_wholesale=item['product'].current_wholesale,
                    )
                    for item in cart_items
                ])

            cart.clear()

            # Email отправляем сразу; для tg/wa ссылку покажем на странице успеха.
            if order.contact_method == Order.ContactMethod.EMAIL:
                notifications.send_order_email(site, order, notifications.build_order_text(order))

            request.session['last_order'] = order.pk
            return redirect('order_success', pk=order.pk)
    else:
        form = OrderForm(allowed_methods=allowed)

    context = {
        **get_common_context(),
        'form': form,
        'cart_items': cart_items,
        'total_retail': total_retail,
        'total_wholesale': total_wholesale,
        'methods': methods,
    }
    return render(request, 'store/checkout.html', context)


def order_success(request, pk):
    # Показываем детали только владельцу заказа (по сессии), чтобы чужой заказ
    # нельзя было открыть перебором id.
    if request.session.get('last_order') != pk:
        return redirect('home')

    order = get_object_or_404(Order, pk=pk)
    site = SiteSettings.load()
    text = notifications.build_order_text(order)

    action_link = None
    if order.contact_method == Order.ContactMethod.TELEGRAM:
        action_link = notifications.telegram_link(site, text)
    elif order.contact_method == Order.ContactMethod.WHATSAPP:
        action_link = notifications.whatsapp_link(site, text)
    elif order.contact_method == Order.ContactMethod.EMAIL:
        action_link = notifications.mailto_link(site, order, text)

    context = {
        **get_common_context(),
        'order': order,
        'action_link': action_link,
    }
    return render(request, 'store/order_success.html', context)


def _safe_back(request):
    """Возврат на предыдущую страницу, но только в пределах своего сайта
    (защита от open-redirect через подделанный Referer)."""
    referer = request.META.get('HTTP_REFERER')
    host = request.get_host()
    if referer:
        parsed = urllib.parse.urlparse(referer)
        if not parsed.netloc or parsed.netloc == host:
            return referer
    return reverse('home')
