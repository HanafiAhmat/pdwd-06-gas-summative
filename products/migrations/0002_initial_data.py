import re
import random
from faker import Faker
from django.db import migrations
from django.template.defaultfilters import slugify
from django.utils import timezone
from libs.commons import convert_markdown_to_html
from libs.genai import get_gemini_response

def initial_categories(apps, schema_editor):
    ProductCategory = apps.get_model("products", "ProductCategory")
    ProductCategory.objects.bulk_create(
        [
            ProductCategory(
                name="General", 
                code="general", 
                short_description="General SmartShop product category", 
                default=True
            ),
        ]
    )

    apparels = ProductCategory.objects.create(
        name="Apparels", 
        code="apparels", 
        short_description="SmartShop Apparels", 
        image='static/img/categories/apparels.avif'
    )
    ProductCategory.objects.bulk_create(
        [
            ProductCategory(
                name="Men Apparels", 
                code="men-apparels", 
                short_description="SmartShop Men Apparels", 
                image='static/img/categories/men-apparel.webp',
                parent=apparels
            ),
            ProductCategory(
                name="Women Apparels", 
                code="women-apparels", 
                short_description="SmartShop Women Apparels", 
                image='static/img/categories/women-apparel.jpg',
                parent=apparels
            ),
        ]
    )

    appliances = ProductCategory.objects.create(
        name="Appliances", 
        code="appliances", 
        short_description="SmartShop Appliances", 
        image='static/img/categories/appliances.jpg'
    )
    ProductCategory.objects.bulk_create(
        [
            ProductCategory(
                name="Kitchen Appliances", 
                code="kitchen-appliances", 
                short_description="SmartShop Kitchen Appliances", 
                image='static/img/categories/kitchen-appliances.jpg',
                parent=appliances
            ),
            ProductCategory(
                name="Home Appliances", 
                code="home-appliances", 
                short_description="SmartShop Home Appliances", 
                image='static/img/categories/home-appliances.jpg',
                parent=appliances
            ),
        ]
    )

    furnitures = ProductCategory.objects.create(
        name="Furnitures", 
        code="furnitures", 
        short_description="SmartShop Furnitures", 
        image='static/img/categories/furnitures.webp'
    )
    ProductCategory.objects.bulk_create(
        [
            ProductCategory(
                name="Living Room Furnitures", 
                code="living-room-furnitures", 
                short_description="SmartShop Living Room Furnitures", 
                image='static/img/categories/Living-Room-Furnitures.webp',
                parent=furnitures
            ),
            ProductCategory(
                name="Bed Room Furnitures", 
                code="bed-room-furnitures", 
                short_description="SmartShop Bed Room Furnitures", 
                image='static/img/categories/Bedroom_furnitures.webp',
                parent=furnitures
            ),
        ]
    )

def initial_brands(apps, schema_editor):
    ProductBrand = apps.get_model("products", "ProductBrand")
    ProductBrand.objects.bulk_create(
        [
            ProductBrand(
                name="H&M", 
                code="h-m", 
                short_description="A Swedish fashion retailer that sells clothing, accessories, homeware, and more.", 
                default=True,
                image="static/img/brands/h-m.svg"
            ),
            ProductBrand(
                name="Ralph Lauren", 
                code="ralph-lauren", 
                short_description="Ralph Lauren Corporation is a global leader in the design, marketing and distribution of luxury lifestyle products.", 
                image="static/img/brands/ralph-lauren.jpg"
            ),
            ProductBrand(
                name="Tommy Hilfiger", 
                code="tommy-hilfiger", 
                short_description="A classic American cool style clothing brand that sells apparel, footwear, accessories, fragrances, and home furnishings.", 
                image="static/img/brands/tommy-hilfiger.jpg"
            ),
            ProductBrand(
                name="Samsung", 
                code="samsung", 
                short_description="A South Korean company that produces a variety of consumer electronics, including mobile phones, televisions, laptops, and memory chips.", 
                image="static/img/brands/samsung.jpg"
            ),
            ProductBrand(
                name="Xiaomi", 
                code="xiaomi", 
                short_description="A Chinese consumer electronics company that designs, manufactures, and sells smartphones, smart hardware, home appliances, and more.", 
                image="static/img/brands/xiaomi.svg"
            ),
            ProductBrand(
                name="Philips", 
                code="philips", 
                short_description="A technology company that cares about people and the planet with meaningful innovations to improved the quality of life for millions of people around the world.", 
                image="static/img/brands/philips.jpg"
            ),
            ProductBrand(
                name="Cellini", 
                code="cellini", 
                short_description="A Singapore home-grown designer furniture brand that designs and curates inspiration for all modern homes.", 
                image="static/img/brands/cellini.png"
            ),
            ProductBrand(
                name="Nitori", 
                code="nitori", 
                short_description="Shop NITORI for well-designed home furniture & home decor in Singapore at affordable prices.", 
                image="static/img/brands/nitori.webp"
            ),
            ProductBrand(
                name="Castilla", 
                code="castilla", 
                short_description="Castilla Furniture Singapore. Luxury quality furniture. Premium furniture. Imported from Italy.", 
                image="static/img/brands/castilla.webp"
            ),
        ]
    )

def initial_themes(apps, schema_editor):
    Theme = apps.get_model("products", "Theme")
    Theme.objects.bulk_create(
        [
            Theme(
                name="Casual", 
                code="casual", 
                short_description="Casual feel", 
            ),
            Theme(
                name="Sports", 
                code="sports", 
                short_description="Sporty appearance", 
            ),
            Theme(
                name="Smart", 
                code="smart", 
                short_description="Smarty allure", 
            ),
            Theme(
                name="Minimalist", 
                code="minimalist", 
                short_description="Minimalist", 
            ),
            Theme(
                name="Zen", 
                code="zen", 
                short_description="Zen serenity", 
            ),
            Theme(
                name="Rustic", 
                code="rustic", 
                short_description="Rustic", 
            ),
            Theme(
                name="Antique", 
                code="antique", 
                short_description="Antique", 
            ),
            Theme(
                name="Classic", 
                code="classic", 
                short_description="Classic", 
            ),
            Theme(
                name="Futuristic", 
                code="futuristic", 
                short_description="Futuristic", 
            ),
        ]
    )

def initial_products(apps, schema_editor):
    ProductBrand = apps.get_model("products", "ProductBrand")
    apparelBrands = [
        ProductBrand.objects.get(code="h-m"),
        ProductBrand.objects.get(code="ralph-lauren"),
        ProductBrand.objects.get(code="tommy-hilfiger")
    ]
    applianceBrands = [
        ProductBrand.objects.get(code="samsung"),
        ProductBrand.objects.get(code="xiaomi"),
        ProductBrand.objects.get(code="philips")
    ]
    furnitureBrands = [
        ProductBrand.objects.get(code="cellini"),
        ProductBrand.objects.get(code="nitori"),
        ProductBrand.objects.get(code="castilla")
    ]

    ProductCategory = apps.get_model("products", "ProductCategory")
    menApparel = ProductCategory.objects.get(code="men-apparels")
    womenApparel = ProductCategory.objects.get(code="women-apparels")
    kitchenAppliance = ProductCategory.objects.get(code="kitchen-appliances")
    homeAppliance = ProductCategory.objects.get(code="home-appliances")
    livingRoomFurniture = ProductCategory.objects.get(code="living-room-furnitures")
    bedRoomFurniture = ProductCategory.objects.get(code="bed-room-furnitures")

    Theme = apps.get_model("products", "Theme")

    fake = Faker()
    Product = apps.get_model("products", "Product")
    productsData = []
    for _ in range(15):
        types = ['Shirt', 'T-shirt', 'Top', 'Hoodie', 'Pants', 'Trousers', 'Pyjama', 'Jeans', 'Cargo Pants', 'Blazer', 'Jacket', 'Suit', 'Shoes', 'Bottom']
        themes = [Theme.objects.order_by('?').first(), Theme.objects.order_by('?').first()]
        name = f'Men {themes[0].name} {random.choice(types)} {fake.sentence(nb_words=1)}'
        brand = random.choice(apparelBrands)
        shortDescription = f'SmartShop {name} by {brand.name}'
        promptMessage = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{name};Product Short Description:{shortDescription};Product Category:{menApparel.short_description};Product Themes:{", ".join([themes[0].name, themes[1].name])};'

        product = Product.objects.create(
            name=name,
            slug=slugify(f'{name}'),
            short_description=shortDescription,
            description=convert_markdown_to_html(get_gemini_response(promptMessage)),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            stock_count=fake.random_int(min=0, max=100),
            created_at=timezone.now(),
            category=menApparel,
            brand=brand,
        )
        product.themes.set(themes)

    for _ in range(15):
        types = ['Shirt', 'T-shirt', 'Top', 'Hoodie', 'Pants', 'Trousers', 'Pyjama', 'Jeans', 'Cargo Pants', 'Dress', 'Jacket', 'Blouse', 'Shoes', 'Bottom']
        themes = [Theme.objects.order_by('?').first(), Theme.objects.order_by('?').first()]
        name = f'Women {themes[0].name} {random.choice(types)} {fake.sentence(nb_words=1)}'
        brand = random.choice(apparelBrands)
        shortDescription = f'SmartShop {name} by {brand.name}'
        promptMessage = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{name};Product Short Description:{shortDescription};Product Category:{womenApparel.short_description};Product Themes:{", ".join([themes[0].name, themes[1].name])};'

        product = Product.objects.create(
            name=name,
            slug=slugify(f'{name}'),
            short_description=shortDescription,
            description=convert_markdown_to_html(get_gemini_response(promptMessage)),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            stock_count=fake.random_int(min=0, max=100),
            created_at=timezone.now(),
            category=womenApparel,
            brand=brand,
        )
        product.themes.set(themes)

    for _ in range(15):
        types = ['Fridge', 'Food Processor', 'Blender', 'Dish Washer', 'Pressure Cooker', 'Coffee Maker', 'Microwave', 'Oven', 'Toaster', 'Bread Maker', 'Dough Mixer', 'Cooker and Hob', 'Rice Cooker', 'Multi-Function Steamer']
        themes = [Theme.objects.order_by('?').first(), Theme.objects.order_by('?').first()]
        name = f'{themes[0].name} {random.choice(types)} {fake.sentence(nb_words=1)}'
        brand = random.choice(applianceBrands)
        shortDescription = f'SmartShop {name} by {brand.name}'
        promptMessage = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{name};Product Short Description:{shortDescription};Product Category:{kitchenAppliance.short_description};Product Themes:{", ".join([themes[0].name, themes[1].name])};'

        product = Product.objects.create(
            name=name,
            slug=slugify(f'{name}'),
            short_description=shortDescription,
            description=convert_markdown_to_html(get_gemini_response(promptMessage)),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            stock_count=fake.random_int(min=0, max=100),
            created_at=timezone.now(),
            category=kitchenAppliance,
            brand=brand,
        )
        product.themes.set(themes)

    for _ in range(15):
        types = ['Television', 'Sound Bar', 'Audio System', 'Air Cooler', 'Air Humidifier', 'Ceiling Fan', 'Washing Machine', 'Air-conditioner', 'Clothes Dryer', 'Garment Steamer', 'Entertainment System', 'Handheld Cordless Vacuum', 'Gaming Console', 'Upholstry Wet Vacuum Cleaner']
        themes = [Theme.objects.order_by('?').first(), Theme.objects.order_by('?').first()]
        name = f'{themes[0].name} {random.choice(types)} {fake.sentence(nb_words=1)}'
        brand = random.choice(applianceBrands)
        shortDescription = f'SmartShop {name} by {brand.name}'
        promptMessage = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{name};Product Short Description:{shortDescription};Product Category:{homeAppliance.short_description};Product Themes:{", ".join([themes[0].name, themes[1].name])};'

        product = Product.objects.create(
            name=name,
            slug=slugify(f'{name}'),
            short_description=shortDescription,
            description=convert_markdown_to_html(get_gemini_response(promptMessage)),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            stock_count=fake.random_int(min=0, max=100),
            created_at=timezone.now(),
            category=homeAppliance,
            brand=brand,
        )
        product.themes.set(themes)

    for _ in range(15):
        types = ['Dining Chair', 'Dining Table', 'Two-Seater Sofa', 'Three-Seater Sofa', 'Corner Three-Seater Sofa', 'Television Console', 'Two Columns Bookcase', 'Three Columns Bookcase', 'Two Tiers Shoe Rack', 'Three Tiers Shoe Rack', 'Square Coffee Table', 'Rectangular Coffee Table', 'Office Desk', 'Showcase Cabinet']
        themes = [Theme.objects.order_by('?').first(), Theme.objects.order_by('?').first()]
        name = f'{themes[0].name} {random.choice(types)} {fake.sentence(nb_words=1)}'
        brand = random.choice(furnitureBrands)
        shortDescription = f'SmartShop {name} by {brand.name}'
        promptMessage = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{name};Product Short Description:{shortDescription};Product Category:{livingRoomFurniture.short_description};Product Themes:{", ".join([themes[0].name, themes[1].name])};'

        product = Product.objects.create(
            name=name,
            slug=slugify(f'{name}'),
            short_description=shortDescription,
            description=convert_markdown_to_html(get_gemini_response(promptMessage)),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            stock_count=fake.random_int(min=0, max=100),
            created_at=timezone.now(),
            category=livingRoomFurniture,
            brand=brand,
        )
        product.themes.set(themes)

    for _ in range(15):
        types = ['Single Bed Metallic Frame', 'Super Single Bed Metallic Frame', 'Queen Bed Metallic Frame', 'King Bed Metallic Frame', 'Single Bed Wooden Frame', 'Super Single Bed Wooden Frame', 'Queen Bed Wooden Frame', 'King Bed Wooden Frame', 'Side Table', 'Dressing Table', 'Lazy Chair', 'Two Door Wardrobe', 'Three Door Wardrobe', 'Sliding Two Door Wardrobe', 'Sliding Three Door Wardrobe']
        themes = [Theme.objects.order_by('?').first(), Theme.objects.order_by('?').first()]
        name = f'{themes[0].name} {random.choice(types)} {fake.sentence(nb_words=1)}'
        brand = random.choice(furnitureBrands)
        shortDescription = f'SmartShop {name} by {brand.name}'
        promptMessage = f'You are an SEO marketing expert. Suggest a comprehensive product description with the following details about the product. Product Name:{name};Product Short Description:{shortDescription};Product Category:{livingRoomFurniture.short_description};Product Themes:{", ".join([themes[0].name, themes[1].name])};'

        product = Product.objects.create(
            name=name,
            slug=slugify(f'{name}'),
            short_description=shortDescription,
            description=convert_markdown_to_html(get_gemini_response(promptMessage)),
            price=fake.pyfloat(left_digits=2, right_digits=2, positive=True),
            stock_count=fake.random_int(min=0, max=100),
            created_at=timezone.now(),
            category=bedRoomFurniture,
            brand=brand,
        )
        product.themes.set(themes)

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(initial_categories),
        migrations.RunPython(initial_brands),
        migrations.RunPython(initial_themes),
        migrations.RunPython(initial_products),
    ]
