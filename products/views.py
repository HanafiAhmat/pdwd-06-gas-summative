import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from libs.commons import build_pagination_data
from libs.genai import smart_search_product, get_review_sentiment
from orders.models import OrderItem
from orders.services.genai import recommend_products_for_user
from .models import Product, ProductCategory, ProductBrand, Theme
from .forms import ProductReviewForm

def get_purchase_history():
    purchases = OrderItem.objects.select_related('order', 'product')
    data = [{
        'user_id': p.order.user.id, 
        'user': p.order.user.email, 
        'product_id': p.product.id, 
        'product': p.product.name, 
        'category': p.product.category.name, 
        'purchase_date': p.order.created_at
    } for p in purchases]
    
    return data

def home(request):
    user = request.user
    purchase_history = get_purchase_history()
    recommendations = recommend_products_for_user(user, purchase_history)
    recommendedProducts = recommendations.all()[0:8] if recommendations is not None else []
    latestProducts = Product.objects.all().order_by('created_at')[0:8]
    popularProducts = OrderItem.objects.annotate(number_of_times_sold=Count('product_id')).order_by('number_of_times_sold')[0:8]
    data = {
        'recommendedProducts': recommendedProducts,
        'recommendedProductsLen': len(recommendedProducts),
        'latestArrivals': latestProducts,
        'latestArrivalsLen': len(latestProducts),
        'popularProducts': popularProducts,
        'popularProductsLen': len(popularProducts),
    }

    return render(request, "products/home.html", data)

def list(request):
    availableCategories = ProductCategory.objects.all()
    selectedCategories = request.GET.getlist('category_ids', availableCategories.values_list('id', flat=True))
    for key in range(len(selectedCategories)):
        if type(selectedCategories[key]) != int:
            selectedCategories[key] = int(selectedCategories[key])

    limit = 9
    pageNum = request.GET.get('page', 1)
    pageNum = int(pageNum)
    stop = pageNum * limit
    start = stop - limit

    pageUrl = reverse('products')
    searchQuery = request.GET.get('s', '')

    featuredProducts = []
    if searchQuery != '' or len(selectedCategories) < len(availableCategories):
        pageUrl += '?'
        totalRecords = Product.objects
        products = Product.objects

        if searchQuery != '':
            pageUrl += 's=' + searchQuery + '&'
            totalRecords = totalRecords.filter(Q(name__icontains=searchQuery) | Q(category__name__icontains=searchQuery))
            products = products.filter(Q(name__icontains=searchQuery) | Q(category__name__icontains=searchQuery))

            featuredProductParams = smart_search_product(searchQuery, 6)
            featuredProductIds = [d['product_id'] for d in featuredProductParams if 'product_id' in d]
            featuredProducts = Product.objects.filter(id__in=featuredProductIds)

        if len(selectedCategories) < len(availableCategories):
            for selectedCategory in selectedCategories:
                pageUrl += 'category_ids=' + str(selectedCategory) + '&'
            totalRecords = totalRecords.filter(category__id__in=selectedCategories)
            products = products.filter(category__id__in=selectedCategories)

        totalRecords = totalRecords.distinct().count()
        products = products.distinct()[start:stop]
    else:
        pageUrl += '?'
        totalRecords = Product.objects.count()
        products = Product.objects.all()[start:stop]

    pagination = build_pagination_data(request, totalRecords, limit, pageUrl)

    data = {
        'featuredProducts': featuredProducts,
        'featuredProductsLen': len(featuredProducts),
        'products': products, 
        'pagination': pagination, 
        'searchQuery': searchQuery, 
        'availableCategories': availableCategories, 
        'selectedCategories': selectedCategories,
        'allCategories': True if len(availableCategories) == len(selectedCategories) else False,
    }
    return render(request, "products/list.html", data)

def detail(request, category_code, slug):
    try:
        product = get_object_or_404(Product, slug=slug)
    except Exception as e:
        product = None
        messages.error(request, 'Requested product is not found.', extra_tags="danger")

    return render(request, 'products/detail.html', {'product': product})

def all_categories(request):
    categories = ProductCategory.objects.all()

    return render(request, "products/all_categories.html", {'categories': categories})

def category_detail(request, code):
    mainCategories = ProductCategory.objects.filter(parent_id=None).all()
    try:
        category = get_object_or_404(ProductCategory, code=code)
    except Exception as e:
        category = None
        messages.error(request, 'Requested product category is not found.', extra_tags="danger")

    return render(request, 'products/category-detail.html', {'mainCategories': mainCategories, 'category': category})

def all_themes(request):
    themes = Theme.objects.all()

    return render(request, "products/all_themes.html", {'themes': themes})

def theme_detail(request, code):
    try:
        theme = get_object_or_404(Theme, code=code)
    except Exception as e:
        theme = None
        messages.error(request, 'Requested product theme is not found.', extra_tags="danger")

    return render(request, 'products/theme-detail.html', {'theme': theme})

def all_brands(request):
    brands = ProductBrand.objects.all()

    return render(request, "products/all_brands.html", {'brands': brands})

def brand_detail(request, code):
    try:
        brand = get_object_or_404(ProductBrand, code=code)
    except Exception as e:
        brand = None
        messages.error(request, 'Requested product brand is not found.', extra_tags="danger")

    return render(request, 'products/brand-detail.html', {'brand': brand})

@login_required(login_url='account_login')
def add_review(request, product_id):
    product = Product.objects.filter(id=product_id).first()
    if product is None:
        messages.error(request, 'Requested product is not found.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if product.user_can_review() is True:
        if product.user_has_reviewed() is True:
            messages.warning(request, 'You have already reviewed this product.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            is_validated = False
            form = ProductReviewForm(initial={'user': request.user, 'product': product})
            if request.method == "POST":
                postData = request.POST.copy()
                postData['user'] = request.user
                postData['product'] = product
                form = ProductReviewForm(postData, request.FILES)
                if form.is_valid():
                    form.save()
                    messages.success(request, f'Review for product {product.name} submitted successfully.')
                    return redirect(f'/products/{product.category.code}/{product.slug}')
                else:
                    is_validated = True
                    dd(form.errors)
                    messages.error(request, 'Error submitting product review.', extra_tags="danger")
    else:
        messages.warning(request, f'You cannot review this product "{product.name}".')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return render(request, "products/review-form.html", {'product': product, 'form': form, 'is_validated': is_validated})
