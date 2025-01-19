"""
URL configuration for assignment4 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from account import views as account_views
from products import views as products_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', account_views.register, name='account_register'),
    path('register/success/', account_views.registration_success, name='account_register_success'),
    path('password-reset-request/', account_views.password_reset_request, name='account_password_reset_request'),
    path('password-reset/<str:token>', account_views.password_reset, name='account_password_reset'),
    path('login/', account_views.user_login, name='account_login'),
    path('logout/', account_views.user_logout, name='account_logout'),
    path('account/', include('account.urls')), 
    path('products/', include('products.urls')), 
    path('categories/<str:code>', products_views.category_detail), 
    path('categories/', products_views.all_categories), 
    path('themes/<str:code>', products_views.theme_detail), 
    path('themes/', products_views.all_themes), 
    path('brands/<str:code>', products_views.brand_detail), 
    path('brands/', products_views.all_brands), 
    path('staff/', include('staff.urls')), 
    path('orders/', include('orders.urls')), 
    path('chatbot/', include('chatbot.urls')), 
    path('', products_views.home, name='home'),
]
