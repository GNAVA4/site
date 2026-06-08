"""Витрина: фильтры, сортировка, пагинация для списков товаров.

Единый механизм для каталога, категории и поиска (логика вынесена из вью).
Поиск передаёт relevance_pks (порядок по rapidfuzz) → доступна сортировка «по релевантности».
Сортировка по цене — по БАЗОВОЙ price_retail (current_* — Python-свойство, в БД не сортируется).
Фильтр «со скидкой» = есть своя ИЛИ категорийная скидка (= Product.has_discount).
"""

from django.core.paginator import Paginator
from django.db.models import Q, Case, When, IntegerField

PAGE_SIZE = 12

# value -> (order_by, подпись для селекта)
SORTS = {
    'new': ('-created_at', 'Сначала новые'),
    'cheap': ('price_retail', 'Сначала дешевле'),
    'expensive': ('-price_retail', 'Сначала дороже'),
    'popular': ('-views', 'Популярные'),
}
DEFAULT_SORT = 'new'

# Товары с действующей скидкой (своей или категорийной).
SALE_Q = Q(discount_percent__gt=0) | Q(category__discount_percent__gt=0)


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def browse(products, request, relevance_pks=None, hide_category=False):
    """Применяет к queryset товаров фильтры/сортировку/пагинацию из request.GET.
    relevance_pks — порядок по релевантности (поиск); тогда доступна сортировка 'relevance'.
    hide_category — не предлагать фильтр по категории (на странице самой категории)."""
    p = request.GET
    allow_relevance = relevance_pks is not None

    requested = p.get('sort')
    if allow_relevance and requested in (None, '', 'relevance'):
        sort = 'relevance'
    elif requested in SORTS:
        sort = requested
    else:
        sort = DEFAULT_SORT

    instock = p.get('instock') == '1'
    sale = p.get('sale') == '1'
    hit = p.get('hit') == '1'
    category = (p.get('category') or '').strip()
    price_min = _to_int(p.get('min'))
    price_max = _to_int(p.get('max'))

    qs = products
    if instock:
        qs = qs.filter(stock__gt=0)
    if sale:
        qs = qs.filter(SALE_Q)
    if hit:
        qs = qs.filter(is_hit=True)
    if category and not hide_category:
        qs = qs.filter(category__slug=category)
    if price_min is not None:
        qs = qs.filter(price_retail__gte=price_min)
    if price_max is not None:
        qs = qs.filter(price_retail__lte=price_max)

    if sort == 'relevance' and allow_relevance:
        # сохраняем порядок выдачи поиска (релевантность)
        order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(relevance_pks)],
                     output_field=IntegerField())
        qs = qs.order_by(order)
    else:
        qs = qs.order_by(SORTS[sort][0], '-id')  # -id — стабильный тай-брейк

    page_obj = Paginator(qs, PAGE_SIZE).get_page(p.get('page'))

    active_filters = sum([
        instock, sale, hit,
        bool(category and not hide_category),
        price_min is not None, price_max is not None,
    ])

    return {
        'products': page_obj.object_list,
        'page_obj': page_obj,
        'sort': sort,
        'sorts': SORTS,
        'allow_relevance': allow_relevance,
        'hide_category_filter': hide_category,
        'f_instock': instock,
        'f_sale': sale,
        'f_hit': hit,
        'f_category': category,
        'f_min': '' if price_min is None else price_min,
        'f_max': '' if price_max is None else price_max,
        'active_filters': active_filters,
        'base_qs': _querystring(p),  # параметры без page — для ссылок пагинации
    }


def _querystring(params):
    """GET-параметры без page — чтобы ссылки пагинации сохраняли фильтры/запрос."""
    q = params.copy()
    q.pop('page', None)
    return q.urlencode()
