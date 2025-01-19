import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity
from django.contrib.auth.models import User
from products.models import Product

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def generate_product_embeddings():
   # Fetch all products from the database
    products = Product.objects.all()

    # Extract product IDs and descriptions
    product_ids = [p.id for p in products]
    descriptions = [p.description for p in products]

    # Generate embeddings using your model
    embeddings = model.encode(descriptions, convert_to_tensor=True)

    # Convert embeddings from tensor to numpy array
    embeddings_list = embeddings.cpu().detach().numpy()

    # Create a DataFrame with embeddings and set product IDs as index
    df = pd.DataFrame(embeddings_list, index=product_ids)

    return df

def recommend_products_for_user(user, purchase_history):
    product_embeddings = generate_product_embeddings()

    # Ensure user is an ID or valid key
    if isinstance(user, User):  # Check if it's a User object
        user_id = user.id  # Extract the ID
    else:
        user_id = user  # Assume it's already an ID

    # Handle empty purchase history
    if purchase_history and len(purchase_history) > 0:
        # Convert QuerySet to DataFrame
        purchase_history_df = pd.DataFrame(purchase_history)
    else:
        purchase_history_df = pd.DataFrame(columns=['user_id', 'user', 'product_id', 'product', 'category', 'purchase_date'])

    # Filter rows for the given user_id
    user_history = purchase_history_df[purchase_history_df['user_id'] == user_id]

    # Extract products the user has interacted with
    purchased_products = user_history['product_id'].tolist() if not user_history.empty else []

    recommended = []
    for product in purchased_products:
        if product not in product_embeddings.index:
            continue

        # Get the embedding vector for the purchased product
        product_vector = product_embeddings.loc[product].values.reshape(1, -1)

        # Compute cosine similarity with all products
        similarity_scores = cosine_similarity(product_vector, product_embeddings.values)

        # Sort and get top 5 similar products
        similar_products = sorted(
            enumerate(similarity_scores[0]),
            key=lambda x: x[1],
            reverse=True
        )
        recommended.extend(
            product_embeddings.index[i] for i, _ in similar_products[:5]
        )

    # Get unique recommendations excluding already purchased products
    recommendations = list(set(recommended) - set(purchased_products))

    # Ensure recommendations are integers if applicable
    recommendations = [int(product_id) for product_id in recommendations if isinstance(product_id, (int, np.integer))]

    # Fetch product details using Django ORM
    if recommendations:
        recommended_products = Product.objects.filter(id__in=recommendations)
    else:
        recommended_products = None

    return recommended_products
