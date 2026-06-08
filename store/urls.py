from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('order/track/', views.track_order, name='track_order'),
    path('privacy/', views.privacy, name='privacy'),
    path('contacts/', views.contacts, name='contacts'),


    # Корзина
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/remove/<str:item_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<str:item_key>/', views.update_cart, name='update_cart'),

    # Оформление заказа
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:pk>/success/', views.order_success, name='order_success'),
]