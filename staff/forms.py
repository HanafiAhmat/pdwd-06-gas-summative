import re
from django.forms import ModelForm, ValidationError, IntegerField, CharField, Select, ChoiceField
from django.template.defaultfilters import slugify
from products.models import Product, ProductCategory, ProductImage, Theme, ProductBrand

class ProductForm(ModelForm):
    category_id = IntegerField()
    brand_id = IntegerField()

    def clean_category_id(self):
        category_id = self.cleaned_data["category_id"]

        if category_id == "":
            raise ValidationError("Category is required.")
        else:
            if ProductCategory.objects.filter(id=category_id).exists() == False:
                raise ValidationError("Selected Category does not exists.")
            else:
                self.cleaned_data["category"] = ProductCategory.objects.get(id=category_id)

        return category_id

    def clean_brand_id(self):
        brand_id = self.cleaned_data["brand_id"]

        if brand_id == "":
            raise ValidationError("Brand is required.")
        else:
            if ProductBrand.objects.filter(id=brand_id).exists() == False:
                raise ValidationError("Selected Brand does not exists.")
            else:
                self.cleaned_data["brand"] = ProductBrand.objects.get(id=brand_id)

        return brand_id

    def clean_slug(self):
        name = self.cleaned_data["name"]
        slug = self.cleaned_data["slug"]

        if slug == "":
            # slug = re.sub(r'[\W_-]', '', name.lower().replace(" ", "-"))
            slug = slugify(name)

        if self.instance is not None:
            if Product.objects.exclude(id=self.instance.id).filter(slug=slug).exists():
                raise ValidationError("The slug must be unique.")
        elif Product.objects.filter(slug=slug).exists():
            raise ValidationError("The slug must be unique.")

        return slug

    # def create(self, validated_data):
    #     if "user" in validated_data:
    #         user = validated_data.pop("user")
    #         user["username"] = user.get("email")
    #         user["password"] = ''.join(random.choices(string.ascii_letters, k=8)), # generate random password 

    #         return VolunteerInfo.objects.create(
    #             user=User.objects.create(**user),
    #             **validated_data,
    #         )

    # def save(self, commit=True):
  
    #     instance = super(Product, self).save(commit=False)
 
    #     # work_set = []
    #     # if instance.id:
    #     #     work_set.extend(instance.works.all())
 
    #     category_id = self.cleaned_data["name"]

    #     if commit:
    #         # self.save_m2m()
    #         instance.save()
    #         # instance.works.add(*work_set)

    #     return instance

    class Meta:
        model = Product
        fields = '__all__'

class ProductCategoryForm(ModelForm):
    parent_id = CharField(required=False)

    def clean_parent_id(self):
        parent_id = self.cleaned_data["parent_id"]

        if parent_id != "":
            if ProductCategory.objects.filter(id=parent_id).exists() == False:
                raise ValidationError("Selected Category does not exists.")
            else:
                self.cleaned_data["parent"] = ProductCategory.objects.get(id=parent_id)

        return parent_id

    def clean_code(self):
        code = self.cleaned_data["code"]

        if self.instance is not None:
            if ProductCategory.objects.exclude(id=self.instance.id).filter(code=code).exists():
                raise ValidationError("The code must be unique.")
        elif ProductCategory.objects.filter(code=code).exists():
            raise ValidationError("The code must be unique.")

        return code

    # def clean(self):
    #     # dump('clean')

    #     name = self.data["name"]

    #     if self.data["code"] == "":
    #         self.data["code"] = re.sub(r'[\W_-]', '', name.lower().replace(" ", "-"))

    #     if self.instance is not None:
    #         if ProductCategory.objects.exclude(id=self.instance.id).filter(code=self.data["code"]).exists():
    #             raise ValidationError("The code must be unique.")
    #     elif ProductCategory.objects.filter(code=self.data["code"]).exists():
    #         raise ValidationError("The code must be unique.")

    #     # dd(self.data)
    #     # Get the user submitted names from the cleaned_data dictionary
    #     cleaned_data = super().clean()
    #     # first_name = cleaned_data.get("first_name")
    #     # last_name = cleaned_data.get("last_name")

    #     # # Check if the first letter of both names is the same
    #     # if first_name[0].lower() != last_name[0].lower():
    #     #     # If not, raise an error
    #     #     raise ValidationError("The first letters of the names do not match")

    #     # if 'no-image.jpg' not in category.image.url:
    #     #     category.image.delete(save=False)

    #     return cleaned_data

    def save(self, commit=True):
        if self.instance is not None:
            if 'no-image.jpg' not in self.instance.image.name and self.cleaned_data['image'].name is not self.instance.image.name:
                self.instance.image.delete(save=False)

        instance = super(ProductCategoryForm, self).save(commit=False)
 
        if commit:
            instance.save()

        return instance

    class Meta:
        model = ProductCategory
        fields = '__all__'
        IS_DEFAULT_CHOICES = (
            ('0', 'No'),
            ('1', 'Yes'),
        )
        widgets = {
            'default': Select(choices=IS_DEFAULT_CHOICES,attrs={'class': 'form-control'}),
        }

class ThemeForm(ModelForm):
    def clean_code(self):
        code = self.cleaned_data["code"]

        if self.instance is not None:
            if Theme.objects.exclude(id=self.instance.id).filter(code=code).exists():
                raise ValidationError("The code must be unique.")
        elif Theme.objects.filter(code=code).exists():
            raise ValidationError("The code must be unique.")

        return code

    class Meta:
        model = Theme
        fields = '__all__'

class ProductBrandForm(ModelForm):
    def clean_code(self):
        code = self.cleaned_data["code"]

        if self.instance is not None:
            if ProductBrand.objects.exclude(id=self.instance.id).filter(code=code).exists():
                raise ValidationError("The code must be unique.")
        elif ProductBrand.objects.filter(code=code).exists():
            raise ValidationError("The code must be unique.")

        return code

    def save(self, commit=True):
        if self.instance is not None:
            if 'no-image.jpg' not in self.instance.image.name and self.cleaned_data['image'].name is not self.instance.image.name:
                self.instance.image.delete(save=False)

        instance = super(ProductBrandForm, self).save(commit=False)
 
        if commit:
            instance.save()

        return instance

    class Meta:
        model = ProductBrand
        fields = '__all__'
        IS_DEFAULT_CHOICES = (
            ('0', 'No'),
            ('1', 'Yes'),
        )
        widgets = {
            'default': Select(choices=IS_DEFAULT_CHOICES,attrs={'class': 'form-control'}),
        }

