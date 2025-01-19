from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('profile', views.profile, name='account_profile'),
    path('profile/update', views.profile_update, name='account_profile_update'),
    path('profile/change-password', views.profile_change_password, name='account_profile_change_password'),
    path('addresses', views.addresses, name="account_addresses"),
    path('addresses/add', views.add_edit_address, name="account_add_address"),
    path('addresses/edit/<int:address_id>', views.add_edit_address, name="account_edit_address"),
    path('addresses/delete/<int:address_id>', views.delete_address),
    path('orders', views.orders, name="account_orders"),
    path('orders/<int:order_id>', views.order_detail),
    path('', views.home, name='account'),
]
