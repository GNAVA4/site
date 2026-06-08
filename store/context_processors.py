from .cart import Cart
from .models import SiteSettings


def site(request):
    """Настройки сайта + сводка корзины во всех шаблонах."""
    cart = Cart(request)
    count = len(cart)
    total = 0
    if count:
        total_retail, _ = cart.totals()
        total = int(total_retail)
    return {
        'site': SiteSettings.load(),
        'cart_count': count,
        'cart_total': total,
    }
