from django.contrib.auth.models import User
from django.db import models
from products.models import Product

class Cart(models.Model):
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name="carts")
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carts'
        ordering = ["created_at"]

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'cart_items'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    recipient_first_name = models.CharField(max_length=120, default=' ')
    recipient_last_name = models.CharField(max_length=120, default=' ')
    recipient_phone = models.CharField(max_length=15, default=' ')
    postcode = models.CharField(max_length=10, default=' ')
    street = models.CharField(max_length=196, default=' ')
    street_optional = models.CharField(max_length=196, default=None, blank=True, null=True)
    building_name = models.CharField(max_length=196, default=None, blank=True, null=True)
    city = models.CharField(max_length=196, default=None, blank=True, null=True)
    state = models.CharField(max_length=196, default=None, blank=True, null=True)
    country = models.CharField(max_length=196, default='Singapore')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'
        ordering = ["created_at"]

    def get_sub_total_price(self):
        return sum(round(float(item['sold_price']) * item['quantity'], 2) for item in self.items.values())

    def no_of_items(self):
        return self.items.count()

    def recipient_fullname(self):
        return str(self.recipient_first_name) + " " + str(self.recipient_last_name)

    def address(self):
        address = f"{self.recipient_fullname()}<br>{self.postcode}<br>"
        if self.state is not None:
            address += f"{self.state} "
        if self.city is not None:
            address += f"{self.city} "
        
        address += f"{self.street}<br>"

        if self.street_optional is not None:
            address += f"{self.street_optional} "
        if self.building_name is not None:
            address += f"{self.building_name} "

        address += f"<br>tel: {self.recipient_phone}"

        return address

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    sold_price = models.FloatField()

    def total_price(self):    
        return round(float(self.sold_price) * self.quantity, 2)

    class Meta:
        db_table = 'order_items'

