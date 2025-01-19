from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='staff'),
    path('order-info/<int:order_id>/', views.order_info, name='staff_order_info'),
    path('list-of-products/', views.list_of_products, name='staff_list_of_products'),
    path('add-product/', views.add_edit_product, name='staff_add_product'),
    path('edit-product/<int:product_id>/', views.add_edit_product),
    path('delete-product/<int:product_id>/', views.delete_product),
    path('suggest-product-description/', views.suggest_product_description, name='staff_suggest_product_description'),
    path('list-of-categories/', views.list_of_categories, name='staff_list_of_categories'),
    path('add-category/', views.add_edit_category, name='staff_add_category'),
    path('edit-category/<int:category_id>/', views.add_edit_category),
    path('delete-category/<int:category_id>/', views.delete_category),
    path('suggest-category-description/', views.suggest_category_description, name='staff_suggest_category_description'),
    path('list-of-themes/', views.list_of_themes, name='staff_list_of_themes'),
    path('add-theme/', views.add_edit_theme, name='staff_add_theme'),
    path('edit-theme/<int:theme_id>/', views.add_edit_theme),
    path('delete-theme/<int:theme_id>/', views.delete_theme),
    path('list-of-brands/', views.list_of_brands, name='staff_list_of_brands'),
    path('add-brand/', views.add_edit_brand, name='staff_add_brand'),
    path('edit-brand/<int:brand_id>/', views.add_edit_brand),
    path('delete-brand/<int:brand_id>/', views.delete_brand),
]
