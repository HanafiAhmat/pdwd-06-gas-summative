from django.db import models
from django.contrib.auth.models import User
from django_currentuser.middleware import get_current_authenticated_user

class ProductCategory(models.Model):
    name = models.CharField(max_length=196)
    code = models.SlugField(unique=True, allow_unicode=True)
    short_description = models.CharField(max_length=160)
    default = models.BooleanField(default=False)
    image = models.ImageField(upload_to='static/img/categories/', default='static/img/categories/no-image.jpg', blank=True, null=True)
    parent = models.ForeignKey('self', default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name="children")

    def no_of_products(self):
        return self.products.count()

    def no_of_children(self):
        return self.children.count()

    def has_children(self):
        if self.children.count() > 0:
            return True
        else:
            return False

    def breadcrumbs(self):
        crumbs = []
        currentCategory = self
        while currentCategory:
          crumbs.append({'label': currentCategory.name, 'url': f'/categories/{currentCategory.code}', 'activeClass': ''})
          currentCategory = currentCategory.parent

        crumbs.reverse()

        return crumbs

    class Meta:
        db_table = 'product_categories'
        ordering = ["name"]

    def __str__(self):
        return str(self.name) + " ["+str(self.code)+"]"

class ProductBrand(models.Model):
    name = models.CharField(max_length=196)
    code = models.SlugField(unique=True, allow_unicode=True)
    short_description = models.CharField(max_length=160)
    default = models.BooleanField(default=False)
    image = models.ImageField(upload_to='static/img/brands/', default='static/img/brands/no-image.jpg', blank=True, null=True)

    def no_of_products(self):
        return self.products.count()

    class Meta:
        db_table = 'product_brands'
        ordering = ["name"]

    def __str__(self):
        return str(self.name) + " ["+str(self.code)+"]"

class Theme(models.Model):
    name = models.CharField(max_length=196)
    code = models.SlugField(unique=True, allow_unicode=True)
    short_description = models.CharField(max_length=160)

    def no_of_products(self):
        return self.product_set.count()

    class Meta:
        db_table = 'themes'
        ordering = ["name"]

    def __str__(self):
        return str(self.name) + " ["+str(self.code)+"]"

class Product(models.Model):
    name = models.CharField(max_length=196)
    slug = models.SlugField(unique=True, allow_unicode=True)
    short_description = models.CharField(max_length=160)
    description = models.TextField()
    price = models.FloatField()
    stock_count = models.IntegerField(default=0)
    category = models.ForeignKey(ProductCategory, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    brand = models.ForeignKey(ProductBrand, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name="products")
    themes = models.ManyToManyField(Theme)
    created_at = models.DateTimeField(default=None, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'products'

    def main_image(self):
        if self.id is None:
            return None
        else:
            return self.images.get(is_main_image=True)

    def additional_images(self):
        if self.id is None:
            return None
        else:
            return self.images.filter(is_main_image=False).all()

    def breadcrumbs(self):
        crumbs = [{'label': self.name, 'url': f'/products/{self.category.code}/{self.slug}', 'activeClass': 'active'}]
        currentCategory = self.category
        while currentCategory:
          crumbs.append({'label': currentCategory.name, 'url': f'/categories/{currentCategory.code}', 'activeClass': ''})
          currentCategory = currentCategory.parent

        crumbs.reverse()

        return crumbs

    def user_can_review(self):
        currentUser = get_current_authenticated_user()

        hasBought = False
        if currentUser is not None:
            if currentUser.orders.filter(items__product_id=self.id).exists():
                hasBought = True

        hasReviewed = False
        if currentUser is not None:
            if currentUser.reviews.filter(product_id=self.id).exists():
                hasReviewed = True

        return hasBought is True and hasReviewed is False

    def user_has_reviewed(self):
        currentUser = get_current_authenticated_user()

        hasReviewed = False
        if currentUser is not None:
            if currentUser.reviews.filter(product_id=self.id).exists():
                hasReviewed = True

        return hasReviewed

    def average_rating(self):
        ratingList = self.reviews.values_list('rating', flat=True)
        return sum(ratingList)/len(ratingList) if len(ratingList) > 0 else 0

    def has_theme(self, theme_id):
        return self.themes.filter(id=theme_id).exists()

    def __str__(self):
        return str(self.name) + " [Price: "+str(self.price)+"]" + " [Stock: "+str(self.stock_count)+"]"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    name = models.CharField(max_length=196)
    url = models.ImageField(upload_to='static/img/products/', default='static/img/products/no-image.jpg', blank=True, null=True)
    is_main_image = models.BooleanField(default=False)

    class Meta:
        db_table = 'product_images'

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.FloatField()
    review = models.TextField()
    sentiment = models.TextField(max_length=50, default=None, blank=True, null=True)
    sentiment_score = models.FloatField(default=None, blank=True, null=True)
    image = models.ImageField(upload_to='static/img/product-reviews/', default='static/img/product-reviews/no-image.jpg', blank=True, null=True)
    
    class Meta:
        db_table = 'product_reviews'
