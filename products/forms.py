from django.forms import ModelForm, ValidationError, IntegerField
from django.contrib.auth.models import User
from products.models import Product, ProductCategory, ProductImage, ProductReview
from libs.genai import get_review_sentiment

class ProductReviewForm(ModelForm):
    # def clean(self):
    # def clean_sentiment(self):
    def clean(self):
        review = self.cleaned_data["review"]
        sentiment = get_review_sentiment(review)

        self.cleaned_data["sentiment"] = sentiment['label']
        self.cleaned_data["sentiment_score"] = sentiment['score']
        
        return self.cleaned_data

    class Meta:
        model = ProductReview
        fields = '__all__'
