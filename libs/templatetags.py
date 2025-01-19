import time
from django import template
from products.models import Product

register = template.Library()

@register.simple_tag
def get_version():
    version = int(round(time.time() * 1000))
    return version

@register.filter() 
def get_table_row_num(value, index):
    return value + index

@register.filter() 
def product_has_theme(product_id, theme_id):
    product = Product.objects.filter(id=product_id).first()
    if product:
        return product.has_theme(theme_id)
    else:
        return False
