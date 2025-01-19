from decimal import *
from products.models import Product
from orders.models import Cart as DBCart, CartItem

class Cart(object):
    def __init__(self, request):
        self.cart_session_id = 'cart'
        self.user = request.user
        self.session = request.session
        cart = self.session.get(self.cart_session_id)
        if not cart:
            if self.user.id is None:
                dbCart = DBCart.objects.filter(session_key=self.session.session_key).first()
            else:
                dbCart = DBCart.objects.filter(user_id=self.user.id).first()

            if dbCart is None:
                # save an empty cart in the session
                cart = self.session[self.cart_session_id] = {}
            else:
                items = {}
                for item in dbCart.items.all():
                    items[item.product.id] = {'quantity': item.quantity, 'price': str(item.product.price), 'name': str(item.product.name)}
                
                cart = self.session[self.cart_session_id] = items

        self.items = cart

    def add(self, product, quantity=1, override_quantity=False):
        product_id = str(product.id)
        if product_id not in self.items:
            self.items[product_id] = {'quantity': 0, 'price': str(product.price), 'name': str(product.name)}

        if override_quantity:
            self.items[product_id]['quantity'] = int(quantity)
        else:
            self.items[product_id]['quantity'] += int(quantity)
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.items:
            del self.items[product_id]
        self.save()

    def clear(self):
        """
        Remove all items from the cart.
        """
        for key in list(self.items.keys()):  # Use list() to create a copy of keys
            del self.items[key]
        self.save()

    def save(self):
        self.session[self.cart_session_id] = self.items

        if self.user.id is None:
            dbCart = DBCart.objects.filter(session_key=self.session.session_key).first()
        else:
            dbCart = DBCart.objects.filter(user_id=self.user.id).first()

        if dbCart is None:
            dbCart = DBCart.objects.create(user_id=self.user.id, session_key=self.session.session_key)
        else:
            dbCart.items.all().delete()

        for productId in self.items:
            ci = CartItem.objects.create(
                cart=dbCart, 
                product_id=int(productId),
                quantity=int(self.items[productId]['quantity']),
            )

    def has_items(self):
        return True if sum(int(item['quantity']) for item in self.items.values()) > 0 else False

    def no_of_items(self):
        return len(self.items)

    def get_sub_total_price(self):
        return round(sum(float(item['price']) * int(item['quantity']) for item in self.items.values()), 2)

    def __iter__(self):
        product_ids = self.items.keys()
        # get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        cart = self.items.copy()

        for product in products:
            cart[str(product.id)]['product'] = product

        for item in cart.values():
            item['price'] = round(float(item['price']), 2)
            item['total_price'] = round(float(item['price']) * int(item['quantity']), 2)
            yield item

    def __len__(self):
        return sum(int(item['quantity']) for item in self.items.values())

