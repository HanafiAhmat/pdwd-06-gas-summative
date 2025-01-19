from django.conf import settings
from products.models import ProductCategory, ProductBrand, Theme

def main_categories(request):
    return {
        'main_categories': ProductCategory.objects.filter(parent_id=None).all()
    }

def brands(request):
    return {
        'brands': ProductBrand.objects.all()
    }

def themes(request):
    return {
        'themes': Theme.objects.all()
    }

def no_of_cart_items(request):
    return {
        'no_of_cart_items': request.cart.no_of_items
    }
