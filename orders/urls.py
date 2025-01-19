from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('add-to-cart/<int:product_id>', views.add_to_cart),
    path('remove-from-cart/<int:product_id>', views.remove_from_cart),
    path('checkout/update-cart-items-quantity', views.update_cart_items_quantity, name="orders_update_cart_items_quantity"),
    path('checkout', views.view_checkout, name="orders_view_checkout"),
]
