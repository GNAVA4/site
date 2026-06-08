from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .cart import Cart
from .models import Category, Product, ProductImage, Order, OrderItem, SiteSettings, DiscountTarget


def make_product(stock=10, price=1000):
    # get_or_create, чтобы повторный вызов в одном тесте не падал на UNIQUE slug.
    cat, _ = Category.objects.get_or_create(slug="test", defaults={"name": "Тест"})
    return Product.objects.create(
        category=cat, title="Матрас", image="products/x.jpg",
        price_retail=price, price_wholesale=price - 100, stock=stock,
    )


class CartLogicTests(TestCase):
    def setUp(self):
        self.product = make_product(stock=5, price=1000)

    def _cart(self):
        # Cart берёт request.session; имитируем через request с сессией клиента.
        request = type("R", (), {})()
        request.session = self.client.session
        return request

    def test_add_keeps_underscore_size_and_caps_stock(self):
        req = self._cart()
        cart = Cart(req)
        qty, capped = cart.add(self.product, "200_300", 2)
        self.assertEqual((qty, capped), (2, False))
        qty, capped = cart.add(self.product, "200_300", 999)
        self.assertEqual(qty, 5)  # обрезано до stock
        self.assertTrue(capped)
        items = list(cart)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["size"], "200_300")  # размер с '_' не потерян

    def test_change_quantity_and_remove_at_zero(self):
        req = self._cart()
        cart = Cart(req)
        cart.add(self.product, "Стандарт", 2)
        key = list(cart.cart.keys())[0]
        cart.change(key, -1)
        self.assertEqual(cart.cart[key]["qty"], 1)
        cart.change(key, -1)  # уходит в 0 → удаление
        self.assertEqual(len(cart), 0)

    def test_change_size_moves_and_merges(self):
        req = self._cart()
        cart = Cart(req)
        cart.add(self.product, "A", 2)
        key_a = list(cart.cart.keys())[0]
        cart.change_size(key_a, "B")
        items = list(cart)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["size"], "B")
        self.assertEqual(items[0]["qty"], 2)
        # повторное добавление размера A и смена на B → слияние количеств
        cart.add(self.product, "A", 1)
        key_a2 = [k for k in cart.cart if k.endswith(":A")][0]
        cart.change_size(key_a2, "B")
        items = list(cart)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["qty"], 3)

    def test_discount_price_and_cart_sum(self):
        p = make_product(stock=10, price=1000)
        p.discount_percent = 25
        p.save()
        p.refresh_from_db()  # как в реальном коде: цены приходят из БД как Decimal, а не int в памяти
        self.assertTrue(p.has_discount)
        self.assertEqual(p.current_retail, Decimal('750'))  # 1000 −25%
        # корзина считает по цене со скидкой
        req = self._cart()
        cart = Cart(req)
        cart.add(p, "Стандарт", 2)
        items = list(cart)
        self.assertEqual(items[0]["sum_retail"], Decimal('1500'))

    def test_iter_skips_deleted_product(self):
        req = self._cart()
        cart = Cart(req)
        cart.add(self.product, "Стандарт", 1)
        self.product.delete()
        self.assertEqual(list(cart), [])  # пропавший товар не роняет корзину


class CheckoutFlowTests(TestCase):
    def setUp(self):
        self.product = make_product(stock=10, price=1000)
        s = SiteSettings.load()
        s.telegram_username = 'shopmanager'
        s.save()

    def test_checkout_creates_order_with_price_snapshot(self):
        # добавляем товар через вью
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 3})

        resp = self.client.post(reverse('checkout'), {
            'customer_name': 'Иван',
            'customer_phone': '+79990000000',
            'contact_method': 'telegram',
            'comment': 'побыстрее',
            'consent': 'on',
        }, follow=True)
        # PRG → редирект на страницу успеха, которая рендерится без ошибок
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(any('order_success' in t.name for t in resp.templates if t.name))
        self.assertContains(resp, 't.me')  # deep-link на Telegram присутствует

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer_name, 'Иван')
        self.assertEqual(order.total_retail, Decimal('3000'))
        item = order.items.get()
        self.assertEqual(item.quantity, 3)
        self.assertEqual(item.price_retail, Decimal('1000'))  # снапшот цены
        self.assertEqual(item.product_title, 'Матрас')

        # корзина очищена
        self.assertEqual(self.client.session.get('cart', {}), {})

    def test_price_snapshot_survives_product_price_change(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 1})
        self.client.post(reverse('checkout'), {
            'customer_name': 'Пётр', 'customer_phone': '+70000000000',
            'contact_method': 'callback', 'consent': 'on',
        })
        # меняем цену товара после заказа
        self.product.price_retail = Decimal('9999')
        self.product.save()
        item = OrderItem.objects.get()
        self.assertEqual(item.price_retail, Decimal('1000'))  # снапшот не изменился

    def test_phone_gets_plus7_prefix(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 1})
        self.client.post(reverse('checkout'), {
            'customer_name': 'Аня', 'customer_phone': '968 123 45 67',
            'contact_method': 'callback', 'consent': 'on',
        })
        order = Order.objects.get()
        self.assertEqual(order.customer_phone, '+7 968 123 45 67')

    def test_phone_with_plus_kept_as_is(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 1})
        self.client.post(reverse('checkout'), {
            'customer_name': 'Боб', 'customer_phone': '+7 999 000 00 00',
            'contact_method': 'callback', 'consent': 'on',
        })
        self.assertEqual(Order.objects.get().customer_phone, '+7 999 000 00 00')

    def test_checkout_empty_cart_redirects(self):
        resp = self.client.get(reverse('checkout'))
        self.assertRedirects(resp, reverse('cart_detail'))

    def test_disabled_channel_rejected(self):
        # whatsapp по умолчанию выключен в SiteSettings → форма не примет
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 1})
        resp = self.client.post(reverse('checkout'), {
            'customer_name': 'X', 'customer_phone': '1', 'contact_method': 'whatsapp', 'consent': 'on',
        })
        self.assertEqual(resp.status_code, 200)  # форма с ошибкой, не редирект
        self.assertEqual(Order.objects.count(), 0)

    def test_order_code_and_tracking(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 1})
        self.client.post(reverse('checkout'), {
            'customer_name': 'Гена', 'customer_phone': '79990000000',
            'contact_method': 'callback', 'consent': 'on',
        })
        order = Order.objects.get()
        self.assertTrue(order.code)  # код сгенерирован

        ok = self.client.post(reverse('track_order'), {'number': order.pk, 'code': order.code})
        self.assertContains(ok, 'Заказ #%d' % order.pk)

        bad = self.client.post(reverse('track_order'), {'number': order.pk, 'code': 'WRONGXYZ'})
        self.assertContains(bad, 'не найден')

    def test_checkout_requires_consent(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]),
                         {'size': 'Стандарт', 'quantity': 1})
        resp = self.client.post(reverse('checkout'), {
            'customer_name': 'Без согласия', 'customer_phone': '79990000000',
            'contact_method': 'callback',  # consent не передан
        })
        self.assertEqual(resp.status_code, 200)        # форма не прошла
        self.assertEqual(Order.objects.count(), 0)     # заказ не создан


class SiteSettingsTests(TestCase):
    def test_singleton(self):
        a = SiteSettings.load()
        a.shop_name = "A"
        a.save()
        b = SiteSettings.load()
        self.assertEqual(SiteSettings.objects.count(), 1)
        self.assertEqual(b.shop_name, "A")


class SearchTests(TestCase):
    def setUp(self):
        self.cat_bed = Category.objects.create(name="Матрасы", slug="matrasy")
        self.cat_tool = Category.objects.create(name="Инструмент", slug="instrument")
        self.mattress = Product.objects.create(
            category=self.cat_bed, title="Матрас детский", description="мягкий и удобный",
            image="products/m.jpg", price_retail=1000, price_wholesale=900, stock=5,
        )
        self.drill = Product.objects.create(
            category=self.cat_tool, title="Дрель ударная", description="мощная",
            image="products/d.jpg", price_retail=2000, price_wholesale=1800, stock=5,
        )

    def _search(self, q):
        return self.client.get(reverse('search'), {'q': q})

    def test_case_insensitive_cyrillic(self):
        # регистр кириллицы не важен (нормализация в Python, а не в SQL/SQLite)
        resp = self._search("МАТРАС")
        self.assertContains(resp, "Матрас детский")
        self.assertNotContains(resp, "Дрель ударная")

    def test_search_by_category_name(self):
        resp = self._search("инструмент")
        self.assertContains(resp, "Дрель ударная")
        self.assertNotContains(resp, "Матрас детский")

    def test_partial_word_substring(self):
        # часть слова (подстрока): «матр» → «матрас»
        self.assertContains(self._search("матр"), "Матрас детский")

    def test_typo_fuzzy_match(self):
        # опечатка: «матрос» → «матрас» (Левенштейн = 1, rapidfuzz)
        resp = self._search("матрос")
        self.assertContains(resp, "Матрас детский")
        self.assertNotContains(resp, "Дрель ударная")

    def test_multiword_requires_all(self):
        # оба слова есть только у матраса (AND)
        resp = self._search("матрас детский")
        self.assertContains(resp, "Матрас детский")
        self.assertNotContains(resp, "Дрель ударная")

    def test_no_match_shows_empty(self):
        resp = self._search("телевизор")
        self.assertContains(resp, "ничего не найдено")
        self.assertNotContains(resp, "Матрас детский")

    def test_blank_query_browses_all_with_filters(self):
        resp = self._search("")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "searchFilters")     # панель фильтров присутствует
        self.assertContains(resp, "Матрас детский")    # без запроса показаны все товары
        self.assertContains(resp, "Дрель ударная")


class CategoryDiscountTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Категория", slug="cat-disc")
        # без своей скидки — должен получить скидку категории
        self.plain = Product.objects.create(
            category=self.cat, title="Без скидки", image="products/a.jpg",
            price_retail=1000, price_wholesale=900, stock=10,
        )
        # со своей скидкой — категорийная не должна ни суммироваться, ни заменять
        self.own = Product.objects.create(
            category=self.cat, title="Со скидкой", image="products/b.jpg",
            price_retail=1000, price_wholesale=900, stock=10,
            discount_percent=10, discount_target=DiscountTarget.RETAIL,
        )

    def _reload(self, p):
        return Product.objects.get(pk=p.pk)  # из БД → цены Decimal, как в проде

    def test_no_discount_full_price(self):
        p = self._reload(self.plain)
        self.assertFalse(p.has_discount)
        self.assertEqual(p.current_retail, Decimal('1000'))

    def test_category_discount_applies_when_product_has_none(self):
        self.cat.discount_percent = 20
        self.cat.save()
        p = self._reload(self.plain)
        self.assertTrue(p.has_discount)
        self.assertEqual(p.effective_discount_percent, 20)
        self.assertEqual(p.current_retail, Decimal('800'))  # 1000 −20%

    def test_own_discount_wins_and_does_not_stack(self):
        self.cat.discount_percent = 50
        self.cat.discount_target = DiscountTarget.BOTH
        self.cat.save()
        p = self._reload(self.own)
        # своя 10% важнее категорийной 50% и НЕ суммируется (не −60% и не −50%)
        self.assertEqual(p.effective_discount_percent, 10)
        self.assertEqual(p.current_retail, Decimal('900'))

    def test_category_discount_target_wholesale_only(self):
        self.cat.discount_percent = 10
        self.cat.discount_target = DiscountTarget.WHOLESALE
        self.cat.save()
        p = self._reload(self.plain)
        self.assertTrue(p.wholesale_discounted)
        self.assertFalse(p.retail_discounted)
        self.assertEqual(p.current_retail, Decimal('1000'))      # розница не тронута
        self.assertEqual(p.current_wholesale, Decimal('810'))    # 900 −10%

    def test_category_discount_flows_into_cart_total(self):
        self.cat.discount_percent = 20
        self.cat.save()
        request = type("R", (), {})()
        request.session = self.client.session
        cart = Cart(request)
        cart.add(self._reload(self.plain), "Стандарт", 2)
        items = list(cart)
        self.assertEqual(items[0]["sum_retail"], Decimal('1600'))  # 800 ×2

    def test_wholesale_only_discount_hides_retail_badge(self):
        # отдельная категория/товар (без «похожих»), чтобы рендер не цеплял чужие бейджи
        cat = Category.objects.create(name="ОптКат", slug="opt-cat",
                                      discount_percent=15, discount_target=DiscountTarget.WHOLESALE)
        p = Product.objects.create(category=cat, title="ОптТовар", image="products/c.jpg",
                                   price_retail=1000, price_wholesale=900, stock=10)
        # скидка только на опт → у розничной цены НЕ должно быть −N% бейджа
        self.assertNotContains(self.client.get(reverse('product_detail', args=[p.pk])), 'badge-disc')
        # переключаем на розницу → бейдок появляется
        cat.discount_target = DiscountTarget.RETAIL
        cat.save()
        self.assertContains(self.client.get(reverse('product_detail', args=[p.pk])), 'badge-disc')


class BrowseTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Кат", slug="kat")
        self.cheap = Product.objects.create(category=self.cat, title="Дешёвый", image="p/1.jpg",
            price_retail=100, price_wholesale=90, stock=5)
        self.mid = Product.objects.create(category=self.cat, title="Средний", image="p/2.jpg",
            price_retail=500, price_wholesale=450, stock=0)        # нет в наличии
        self.pricey = Product.objects.create(category=self.cat, title="Дорогой", image="p/3.jpg",
            price_retail=900, price_wholesale=800, stock=5, discount_percent=10)  # со скидкой

    def test_sort_cheap_first(self):
        resp = self.client.get(reverse('catalog'), {'sort': 'cheap'})
        prices = [p.price_retail for p in resp.context['products']]
        self.assertEqual(prices, sorted(prices))
        self.assertEqual(resp.context['products'][0], self.cheap)

    def test_sort_expensive_first(self):
        resp = self.client.get(reverse('catalog'), {'sort': 'expensive'})
        self.assertEqual(resp.context['products'][0], self.pricey)

    def test_filter_instock_excludes_out_of_stock(self):
        items = list(self.client.get(reverse('catalog'), {'instock': '1'}).context['products'])
        self.assertIn(self.cheap, items)
        self.assertNotIn(self.mid, items)

    def test_filter_sale_only_discounted(self):
        items = list(self.client.get(reverse('catalog'), {'sale': '1'}).context['products'])
        self.assertEqual(items, [self.pricey])

    def test_price_range(self):
        items = list(self.client.get(reverse('catalog'), {'min': '200', 'max': '800'}).context['products'])
        self.assertEqual(items, [self.mid])

    def test_pagination_second_page(self):
        for i in range(12):  # +12 к 3 из setUp = 15; PAGE_SIZE=12 → 2 страницы
            Product.objects.create(category=self.cat, title=f"T{i}", image="p/x.jpg",
                price_retail=300, price_wholesale=250, stock=3)
        resp = self.client.get(reverse('catalog'), {'page': '2'})
        self.assertEqual(resp.context['page_obj'].number, 2)
        self.assertEqual(len(resp.context['products']), 3)


class SearchFilterTests(TestCase):
    def setUp(self):
        self.cat1 = Category.objects.create(name="Матрасы", slug="matr")
        self.cat2 = Category.objects.create(name="Инструмент", slug="instr")
        # все содержат слово «товар» → находятся одним поисковым запросом
        self.a = Product.objects.create(category=self.cat1, title="Товар матрас", image="p/a.jpg",
            price_retail=100, price_wholesale=90, stock=5, discount_percent=10)   # со скидкой
        self.b = Product.objects.create(category=self.cat1, title="Товар подушка", image="p/b.jpg",
            price_retail=500, price_wholesale=450, stock=0, is_hit=True)           # нет в наличии, хит
        self.c = Product.objects.create(category=self.cat2, title="Товар дрель", image="p/c.jpg",
            price_retail=900, price_wholesale=800, stock=5)

    def _products(self, **params):
        params['q'] = 'товар'
        return list(self.client.get(reverse('search'), params).context['products'])

    def test_search_returns_all_matches(self):
        self.assertCountEqual(self._products(), [self.a, self.b, self.c])

    def test_filter_instock(self):
        items = self._products(instock='1')
        self.assertIn(self.a, items)
        self.assertNotIn(self.b, items)  # b нет в наличии

    def test_filter_sale(self):
        self.assertEqual(self._products(sale='1'), [self.a])

    def test_filter_hit(self):
        self.assertEqual(self._products(hit='1'), [self.b])

    def test_filter_category(self):
        self.assertEqual(self._products(category='instr'), [self.c])

    def test_filter_price_range(self):
        self.assertEqual(self._products(min='200', max='800'), [self.b])

    def test_sort_cheap(self):
        prices = [p.price_retail for p in self._products(sort='cheap')]
        self.assertEqual(prices, sorted(prices))


class ProductGalleryTests(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(name="Г", slug="g")
        self.product = Product.objects.create(category=self.cat, title="Товар", image="products/cover.jpg",
            price_retail=1000, price_wholesale=900, stock=5)

    def test_gallery_includes_cover_and_extras(self):
        ProductImage.objects.create(product=self.product, image="products/extra1.jpg", sort=1)
        ProductImage.objects.create(product=self.product, image="products/extra2.jpg", sort=2)
        gallery = self.product.gallery
        self.assertEqual(len(gallery), 3)  # обложка + 2 доп.
        self.assertEqual(gallery[0], self.product.image)  # обложка первая

    def test_single_image_no_carousel(self):
        resp = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertNotContains(resp, 'productGallery')
        self.assertContains(resp, 'pg-single')

    def test_multiple_images_render_carousel(self):
        ProductImage.objects.create(product=self.product, image="products/extra1.jpg")
        resp = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertContains(resp, 'productGallery')
        self.assertContains(resp, 'pg-thumbs')
