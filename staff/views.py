import re
import json
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from libs.commons import build_pagination_data, send_email, convert_markdown_to_html
from libs.genai import get_gemini_response
from products.models import Product, ProductImage, ProductCategory, Theme, ProductBrand, ProductReview
from orders.models import Order
from .forms import ProductForm, ProductCategoryForm, ThemeForm, ProductBrandForm

@staff_member_required(login_url='account_login')
def home(request):
    orders = Order.objects.all().order_by('-created_at')
    reviews = ProductReview.objects
    totalReviews = reviews.count()
    reviewSummary = {
        'totalReviews': totalReviews,
        'totalPositive': reviews.filter(sentiment='POSITIVE').count(),
        'totalNegative': reviews.filter(sentiment='NEGATIVE').count(),
        'averageSentimentScore': round(reviews.aggregate(Avg('sentiment_score'))['sentiment_score__avg'] * 100, 2),
    }

    return render(request, 'staff/home.html', {'orders': orders, 'reviewSummary': reviewSummary})

@staff_member_required(login_url='account_login')
def order_info(request, order_id):
    order = Order.objects.filter(id=order_id).first()
    if order is None:
        messages.error(request, 'Requested order does not exists.', extra_tags="danger")
        return redirect('staff')

    return render(request, 'staff/order-info.html', {'order': order})

@staff_member_required(login_url='account_login')
def list_of_products(request):
    limit = 25
    pageNum = request.GET.get('page', 1)
    pageNum = int(pageNum)
    stop = pageNum * limit
    start = stop - limit

    products = Product.objects.all()[start:stop]
    totalRecords = Product.objects.count()

    pageUrl = reverse('staff_list_of_products') + '?'

    pagination = build_pagination_data(request, totalRecords, limit, pageUrl)

    return render(request, 'staff/list-of-products.html', {'products': products, 'pagination': pagination})

@staff_member_required(login_url='account_login')
def add_edit_product(request, product_id=None):
    is_validated = False
    availableCategories = ProductCategory.objects.all().order_by('name')
    availableThemes = Theme.objects.all().order_by('name')
    availableBrands = ProductBrand.objects.all().order_by('name')
    if product_id is None:
        mode = 'Add'
        product = Product()
        form = ProductForm()
    else:
        mode = 'Edit'
        try:
            product = get_object_or_404(Product, id=product_id)
            form = ProductForm(instance=product)
        except Exception as e:
            messages.error(request, 'Requested product to be updated does not exists.', extra_tags="danger")
            return redirect('staff_list_of_products')

    if request.method == "POST":
        postData = request.POST.copy()
        if postData.get('slug', '') == '':
            postData['slug'] = slugify(postData['name'])
        form = ProductForm(postData, instance=product)
        if form.is_valid():
            product = form.save()

            themeIds = postData.getlist('themes')
            product.themes.clear()
            for themeId in themeIds:
                theme = Theme.objects.get(id=themeId)
                product.themes.add(theme)
            product.save()

            main_image = request.FILES.get('main_image', False)
            additional_images = request.FILES.getlist('additional_images', False)
            if mode == 'Edit':
                if main_image is not False and form.instance.main_image is not None:
                    instanceMainImage = form.instance.main_image()
                    instanceMainImage.url.delete(save=False)
                    instanceMainImage.delete()

            if main_image is not False:
                ProductImage.objects.create(
                    product=product,
                    name=main_image.name,
                    url=main_image,
                    is_main_image=True
                )

            if additional_images is not False:
                if mode == 'Edit':
                    for addedImage in form.instance.additional_images():
                        toRetain = False
                        for image in additional_images:
                            if image.name == addedImage.name:
                                toRetain = True
                                additional_images.remove(image)

                        if toRetain == False:
                            addedImage.url.delete(save=False)
                            addedImage.delete()

                for image in additional_images:
                    ProductImage.objects.create(
                        product=product,
                        name=image.name,
                        url=image,
                        is_main_image=False
                    )

            if mode == 'Add':
                messages.success(request, 'Product added successfully')
            else:
                messages.success(request, 'Product updated successfully')
            return redirect('staff_list_of_products')
        else:
            is_validated = True
            dd(form.errors)
            messages.error(request, 'Error creating new product.', extra_tags="danger")

    data = {
        'mode': mode, 
        'availableCategories': availableCategories,
        'availableThemes': availableThemes,
        'availableThemesLen': len(availableThemes),
        'availableBrands': availableBrands,
        'product': product, 
        'form': form,
        'is_validated': is_validated
    }
    return render(request, 'staff/product-form.html', data)

@staff_member_required(login_url='account_login')
def delete_product(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
    except Exception as e:
        messages.error(request, 'Requested product to be deleted does not exists.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_products'))

    hasLoanRecord = False
    # for productCopy in product.product_copies():
    #     if productCopy.loan_set.count() > 0:
    #         hasLoanRecord = True
    #         break

    productTitle = product.title
    if hasLoanRecord == True:
        messages.error(request, f'Requested product `{productTitle}` cannot be deleted due to having loan record(s).', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_products'))
    else:
        product.delete()
        messages.success(request, f'Product `{productTitle}` deleted successfully')
        return redirect('staff_list_of_products')

@staff_member_required(login_url='account_login')
@csrf_protect
def suggest_product_description(request):
    if request.method == "POST":
        postData = json.loads(request.body)
        user_message = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{postData.get('name')};Product Category:{postData.get('category')};Product Short Description:{postData.get('short_description')}'
        result = convert_markdown_to_html(get_gemini_response(user_message))
        return JsonResponse({'result': result}, status=200)

    return JsonResponse({'result': request.method}, status=200)

@staff_member_required(login_url='account_login')
def list_of_categories(request):
    limit = 25
    pageNum = request.GET.get('page', 1)
    pageNum = int(pageNum)
    stop = pageNum * limit
    start = stop - limit

    categories = ProductCategory.objects.all()[start:stop]
    totalRecords = ProductCategory.objects.count()

    pageUrl = reverse('staff_list_of_categories') + '?'

    pagination = build_pagination_data(request, totalRecords, limit, pageUrl)

    return render(request, 'staff/list-of-categories.html', {'categories': categories, 'pagination': pagination})

@staff_member_required(login_url='account_login')
def add_edit_category(request, category_id=None):
    is_validated = False
    availableCategories = ProductCategory.objects.all().order_by('name')
    if category_id is None:
        mode = 'Add'
        category = ProductCategory()
        form = ProductCategoryForm()
    else:
        mode = 'Edit'
        try:
            category = get_object_or_404(ProductCategory, id=category_id)
            form = ProductCategoryForm(instance=category)
        except Exception as e:
            messages.error(request, 'Requested category to be updated does not exists.', extra_tags="danger")
            return redirect('staff_list_of_categories')

    if request.method == "POST":
        postData = request.POST.copy()
        if postData.get('code', '') == '':
            postData['code'] = slugify(postData['name'])
        form = ProductCategoryForm(postData, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()

            if mode == 'Add':
                messages.success(request, 'Product Category added successfully')
            else:
                messages.success(request, 'Product Category updated successfully')
            return redirect('staff_list_of_categories')
        else:
            is_validated = True
            messages.error(request, 'Error creating new category.', extra_tags="danger")

    data = {
        'mode': mode, 
        'availableCategories': availableCategories, 
        'form': form,
        'is_validated': is_validated
    }
    return render(request, 'staff/category-form.html', data)

@staff_member_required(login_url='account_login')
def delete_category(request, category_id):
    try:
        category = get_object_or_404(ProductCategory, id=category_id)
    except Exception as e:
        messages.error(request, 'Requested category to be deleted does not exists.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_categories'))

    numOfProducts = category.products.count()
    numOfChildren = category.children.count()

    categoryName = category.name
    if numOfProducts > 0:
        messages.error(request, f'Requested category `{categoryName}` cannot be deleted due to having <b>{numOfProducts}</b> product(s) assigned to it.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_categories'))
    elif numOfChildren == True:
        messages.error(request, f'Requested category `{categoryName}` cannot be deleted due to having <b>{numOfChildren}</b> child category assigned to it.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_categories'))
    else:
        if 'no-image.jpg' not in category.image.url:
            category.image.delete(save=False)
        category.delete()
        messages.success(request, f'Product Category `{categoryName}` deleted successfully')
        return redirect('staff_list_of_categories')

@staff_member_required(login_url='account_login')
@csrf_protect
def suggest_category_description(request):
    if request.method == "POST":
        postData = json.loads(request.body)
        user_message = f'You are an SEO marketing expert. Suggest a comprehensive product category description with the following details about the category. Category Name:{postData.get('name')};Category Short Description:{postData.get('short_description')}'
        result = convert_markdown_to_html(get_gemini_response(user_message))
        return JsonResponse({'result': result}, status=200)

    return JsonResponse({'result': request.method}, status=200)

@staff_member_required(login_url='account_login')
def list_of_themes(request):
    limit = 25
    pageNum = request.GET.get('page', 1)
    pageNum = int(pageNum)
    stop = pageNum * limit
    start = stop - limit

    themes = Theme.objects.all()[start:stop]
    totalRecords = Theme.objects.count()

    pageUrl = reverse('staff_list_of_themes') + '?'

    pagination = build_pagination_data(request, totalRecords, limit, pageUrl)

    return render(request, 'staff/list-of-themes.html', {'themes': themes, 'pagination': pagination})

@staff_member_required(login_url='account_login')
def add_edit_theme(request, theme_id=None):
    is_validated = False
    if theme_id is None:
        mode = 'Add'
        theme = Theme()
        form = ThemeForm()
    else:
        mode = 'Edit'
        try:
            theme = get_object_or_404(Theme, id=theme_id)
            form = ThemeForm(instance=theme)
        except Exception as e:
            messages.error(request, 'Requested theme to be updated does not exists.', extra_tags="danger")
            return redirect('staff_list_of_themes')

    if request.method == "POST":
        postData = request.POST.copy()
        if postData.get('code', '') == '':
            postData['code'] = slugify(postData['name'])
        form = ThemeForm(postData, instance=theme)
        if form.is_valid():
            theme = form.save()

            if mode == 'Add':
                messages.success(request, 'Theme added successfully')
            else:
                messages.success(request, 'Theme updated successfully')
            return redirect('staff_list_of_themes')
        else:
            is_validated = True
            messages.error(request, 'Error creating new theme.', extra_tags="danger")

    data = {
        'mode': mode, 
        'form': form,
        'is_validated': is_validated
    }
    return render(request, 'staff/theme-form.html', data)

@staff_member_required(login_url='account_login')
def delete_theme(request, theme_id):
    try:
        theme = get_object_or_404(Theme, id=theme_id)
    except Exception as e:
        messages.error(request, 'Requested theme to be deleted does not exists.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_themes'))

    theme.delete()
    messages.success(request, f'Theme `{themeName}` deleted successfully')
    return redirect('staff_list_of_themes')

@staff_member_required(login_url='account_login')
def list_of_brands(request):
    limit = 25
    pageNum = request.GET.get('page', 1)
    pageNum = int(pageNum)
    stop = pageNum * limit
    start = stop - limit

    brands = ProductBrand.objects.all()[start:stop]
    totalRecords = ProductBrand.objects.count()

    pageUrl = reverse('staff_list_of_brands') + '?'

    pagination = build_pagination_data(request, totalRecords, limit, pageUrl)

    return render(request, 'staff/list-of-brands.html', {'brands': brands, 'pagination': pagination})

@staff_member_required(login_url='account_login')
def add_edit_brand(request, brand_id=None):
    is_validated = False
    availableBrands = ProductBrand.objects.all().order_by('name')
    if brand_id is None:
        mode = 'Add'
        brand = ProductBrand()
        form = ProductBrandForm()
    else:
        mode = 'Edit'
        try:
            brand = get_object_or_404(ProductBrand, id=brand_id)
            form = ProductBrandForm(instance=brand)
        except Exception as e:
            messages.error(request, 'Requested brand to be updated does not exists.', extra_tags="danger")
            return redirect('staff_list_of_brands')

    if request.method == "POST":
        postData = request.POST.copy()
        if postData.get('code', '') == '':
            postData['code'] = slugify(postData['name'])
        form = ProductBrandForm(postData, request.FILES, instance=brand)
        if form.is_valid():
            brand = form.save()

            if mode == 'Add':
                messages.success(request, 'Product Brand added successfully')
            else:
                messages.success(request, 'Product Brand updated successfully')
            return redirect('staff_list_of_brands')
        else:
            is_validated = True
            messages.error(request, 'Error creating new brand.', extra_tags="danger")

    data = {
        'mode': mode, 
        'availableBrands': availableBrands, 
        'form': form,
        'is_validated': is_validated
    }
    return render(request, 'staff/brand-form.html', data)

@staff_member_required(login_url='account_login')
def delete_brand(request, brand_id):
    try:
        brand = get_object_or_404(ProductBrand, id=brand_id)
    except Exception as e:
        messages.error(request, 'Requested brand to be deleted does not exists.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_brands'))

    numOfProducts = brand.products.count()

    brandName = brand.name
    if numOfProducts > 0:
        messages.error(request, f'Requested brand `{brandName}` cannot be deleted due to having <b>{numOfProducts}</b> product(s) assigned to it.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'staff_list_of_brands'))
    else:
        if 'no-image.jpg' not in brand.image.url:
            brand.image.delete(save=False)
        brand.delete()
        messages.success(request, f'Product Brand `{brandName}` deleted successfully')
        return redirect('staff_list_of_brands')











