"""Корзина в сессии.

Хранит позиции структурой, а НЕ строкой "ID_SIZE" — старый код парсил ключ
через split('_'), что ломалось на размерах с '_' и на удалённых товарах
(падал весь cart_detail с 500). Здесь ключ используется только как
идентификатор позиции, а product_id/size/qty хранятся явными полями.

Структура в session['cart']:
    { "<key>": {"product_id": int, "size": str, "qty": int}, ... }
"""

from decimal import Decimal

from .models import Product

CART_SESSION_KEY = 'cart'


def _make_key(product_id, size):
    # ':' как разделитель только для генерации ключа; обратно мы его НЕ парсим.
    return f"{product_id}:{size}"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if not isinstance(cart, dict):
            cart = {}
        self.cart = cart

    def _save(self):
        self.session[CART_SESSION_KEY] = self.cart
        self.session.modified = True

    def add(self, product, size, qty):
        """Добавляет qty штук. Возвращает (итоговое_кол-во, capped):
        capped=True, если количество обрезано остатком на складе."""
        key = _make_key(product.id, size)
        current = self.cart.get(key, {}).get('qty', 0)
        desired = current + qty
        # Не даём заказать больше, чем есть на складе.
        new_qty = min(desired, product.stock)
        capped = new_qty < desired
        if new_qty < 1:
            return 0, capped
        self.cart[key] = {'product_id': product.id, 'size': size, 'qty': new_qty}
        self._save()
        return new_qty, capped

    def set_qty(self, key, qty):
        """Устанавливает точное количество позиции (с учётом склада).
        qty < 1 или пропавший товар → позиция удаляется."""
        item = self.cart.get(key)
        if not item:
            return
        if qty < 1:
            self.remove(key)
            return
        product = Product.objects.filter(pk=item['product_id'], is_active=True).first()
        if product is None:
            self.remove(key)
            return
        item['qty'] = min(qty, product.stock)
        self.cart[key] = item
        self._save()

    def change(self, key, delta):
        """Меняет количество на delta (например +1 / -1)."""
        item = self.cart.get(key)
        if item:
            self.set_qty(key, item['qty'] + delta)

    def change_size(self, key, new_size):
        """Меняет размер позиции. Технически это новый ключ product_id:size,
        поэтому переносим количество на новый ключ (сливая, если такой уже есть)."""
        item = self.cart.get(key)
        if not item or new_size == item['size']:
            return
        new_key = _make_key(item['product_id'], new_size)
        qty = item['qty']
        del self.cart[key]
        if new_key in self.cart:
            self.cart[new_key]['qty'] += qty
        else:
            self.cart[new_key] = {'product_id': item['product_id'], 'size': new_size, 'qty': qty}
        self._save()

    def remove(self, key):
        if key in self.cart:
            del self.cart[key]
            self._save()
            return True
        return False

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.session.modified = True
        self.cart = {}

    def __len__(self):
        return len(self.cart)

    def __iter__(self):
        """Отдаёт позиции с подгруженными товарами ОДНИМ запросом.
        Молча пропускает товары, которых больше нет или которые скрыты."""
        ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(pk__in=ids, is_active=True).select_related('category').prefetch_related('sizes')
        products_by_id = {p.id: p for p in products}

        stale_keys = []
        for key, item in self.cart.items():
            product = products_by_id.get(item['product_id'])
            if product is None:
                stale_keys.append(key)
                continue
            qty = item['qty']
            yield {
                'key': key,
                'product': product,
                'size': item['size'],
                'qty': qty,
                'sum_retail': product.current_retail * qty,
                'sum_wholesale': product.current_wholesale * qty,
            }

        # Подчищаем пропавшие товары, чтобы они не висели в сессии вечно.
        if stale_keys:
            for key in stale_keys:
                del self.cart[key]
            self._save()

    def totals(self):
        total_retail = Decimal('0')
        total_wholesale = Decimal('0')
        for item in self:
            total_retail += item['sum_retail']
            total_wholesale += item['sum_wholesale']
        return total_retail, total_wholesale
