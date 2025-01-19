import json
from django.contrib import messages
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from .models import Order, OrderItem
from products.models import Product
from account.models import CustomerAddress
from account.forms import CustomerAddressForm, RegistrationForm

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.filter(id=product_id).first()
        if product is not None:
            quantity = request.POST.get('quantity', 1)
            request.cart.add(product, quantity, True)
            messages.success(request, f'Product "{product.name}" added to cart.')
        else:
            messages.error(request, 'Requested product is not found.', extra_tags="danger")
    else:
        messages.error(request, 'Unacceptable request.', extra_tags="danger")

    return redirect(request.META.get('HTTP_REFERER', '/'))

@csrf_protect
def update_cart_items_quantity(request):
    if request.method == "POST":
        postData = json.loads(request.body)
        items = postData.get('items', [])
        for item in items:
            product = Product.objects.filter(id=item['product_id']).first()
            if product is not None:
                request.cart.add(product, item['quantity'], True)

    return JsonResponse({'result': True}, status=200)

@csrf_protect
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        product = Product.objects.filter(id=product_id).first()
        if product is None:
            messages.error(request, 'Requested product to be removed from cart does not exists.', extra_tags="danger")
        else:
            request.cart.remove(product)
            messages.success(request, f'"{product.name}" removed from cart successfully')
    else:
        messages.error(request, 'Bad Request.', extra_tags="danger")

    return redirect(request.META.get('HTTP_REFERER', '/'))

def view_checkout(request):
    caform = CustomerAddressForm()
    userform = RegistrationForm()
    is_validated = False
    if request.method == 'POST':
        caform = CustomerAddressForm(request.POST)
        if request.user.is_authenticated:
            user = request.user
        else:
            userData = {
                'first_name':request.POST.get('recipient_first_name'),
                'last_name':request.POST.get('recipient_last_name'),
                'email':request.POST.get('email'),
                'phone':request.POST.get('recipient_phone'),
                'password':request.POST.get('password'),
                'confirm_password':request.POST.get('confirm_password')
            }
            userform = RegistrationForm(userData)
            if userform.is_valid():
                user = userform.save()
                login(request, user)
            else:
                user = None
                is_validated = True
                messages.error(request, 'Something wrong with customer account details.', extra_tags="danger")
                return render(request, "orders/checkout.html", {'cart': request.cart, 'caform': caform, 'userform': userform, 'is_validated': is_validated})

        addressId = request.POST.get('address_id', None)
        if addressId is None:
            userAddressData = {
                'recipient_first_name':request.POST.get('recipient_first_name'),
                'recipient_last_name':request.POST.get('recipient_last_name'),
                'email':request.POST.get('email'),
                'recipient_phone':request.POST.get('recipient_phone'),
                'user':user,
                'postcode':request.POST.get('postcode'),
                'street':request.POST.get('street'),
                'street_optional':request.POST.get('street_optional'),
                'building_name':request.POST.get('building_name'),
                'city':request.POST.get('city'),
                'state':request.POST.get('state'),
                'country':request.POST.get('country'),
                'default':True
            }
            caform = CustomerAddressForm(userAddressData)
            if caform.is_valid():
                customerAddress = caform.save()
            else:
                customerAddress = None
                is_validated = True
                messages.error(request, 'Something wrong with customer address information.', extra_tags="danger")
                return render(request, "orders/checkout.html", {'cart': request.cart, 'caform': caform, 'userform': userform, 'is_validated': is_validated})
        else:
            customerAddress = CustomerAddress.objects.get(id=addressId)

        order = Order.objects.create(
            user=user,
            recipient_first_name=customerAddress.recipient_first_name,
            recipient_last_name=customerAddress.recipient_last_name,
            recipient_phone=customerAddress.recipient_phone,
            postcode=customerAddress.postcode,
            street=customerAddress.street,
            street_optional=customerAddress.street_optional,
            building_name=customerAddress.building_name,
            city=customerAddress.city,
            state=customerAddress.state,
            country=customerAddress.country
        )
        for item in request.cart:
            oi = OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                sold_price=item['price']
            )
            item['product'].stock_count = item['product'].stock_count - item['quantity']
            item['product'].save()

        request.cart.clear()
        messages.success(request, 'You have checkout successfully.')
        return redirect(f"/account/orders/{order.id}")

    return render(request, "orders/checkout.html", {'cart': request.cart, 'caform': caform, 'userform': userform, 'is_validated': is_validated})
