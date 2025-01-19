from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.list, name='products'),
    path('add-review/<int:product_id>', views.add_review),
    path('<str:category_code>/<str:slug>', views.detail, name='products_product_detail'),
]
