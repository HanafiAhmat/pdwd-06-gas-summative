import requests
from transformers import AutoModel, AutoTokenizer, pipeline
from sklearn.metrics.pairwise import cosine_similarity
from django.conf import settings
from products.models import ProductCategory, ProductBrand, Theme, Product

# Load a lightweight pre-trained model (e.g., 'sentence-transformers/all-MiniLM-L6-v2')
model_name = "sentence-transformers/all-MiniLM-L6-v2" 
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + settings.GEMINI_API_KEY

def query_gemini(payload):
    headers = {
        # "Authorization": f"Bearer {API_KEY}", # for OAuth authentication
        "Content-Type": "application/json"
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        # print ("===================================================================")
        # print (response_data)
        # print ("===================================================================")

        # Returning the generated tabular development plan
        text_content = response_data['candidates'][0]['content']['parts'][0]['text']
        # print ("===================================================================")
        # print (text_content)
        # print ("===================================================================")

        return text_content
    else:
        return None

def get_gemini_response(user_message):
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": user_message
                    }
                ]
            }
        ]
    }

    return query_gemini(payload)

def get_gemini_chatbot_response(new_user_message, user_chat_histories=None):
    websiteUrl = settings.WEBSITE_URL

    allCategories = ProductCategory.objects.all()

    instructions = f"You are a Sales Assistance working at SmartShop Online Store located at {websiteUrl}" 
    instructions += f"\nThe store have products under these categories (with url): " 
    for category in allCategories:
        instructions += f"\n- Name: {category.name}; URL: {websiteUrl}/categories/{category.code}; " 
        instructions += f"\n\tThese are the products under {category.name} category (with individual product url): " 
        for product in category.products.all():
            instructions += f"\n\t- Name: {product.name}; Price: ${round(product.price, 2)}; Average Rating: {product.average_rating()}; URL: {websiteUrl}/products/{category.code}/{product.slug}; " 
    
    contents = []
    if user_chat_histories is not None:
        for history in user_chat_histories:
            contents.append({"role": "user", "parts": [{"text": history.user_message}]})
            contents.append({"role": "model", "parts": [{"text": history.bot_response}]})

    contents.append({"role": "user", "parts": [{"text": new_user_message}]})

    # If the threshold is not set, the default block threshold is Block most (for gemini-1.5-pro-002 and gemini-1.5-flash-002 only)
    # or Block some (in all other models) for all categories except the Civic integrity category.
    payload = {
        # "safetySettings": [
        #     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
        #     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
        # ],
        "system_instruction": {
            "parts": { 
                "text": instructions 
            }
        },
        "contents": contents
        # "contents": [
        #     {
        #         "role":"user",
        #         "parts":[{"text": "Hello"}]
        #     },
        #     {
        #         "role": "model",
        #         "parts":[{"text": "Great to meet you. What would you like to know?"}]
        #     },
        #     {
        #         "role":"user",
        #         "parts":[{"text": "I have two dogs in my house. How many paws are in my house?"}]
        #     },
        # ]
    }

    return query_gemini(payload)

def get_review_sentiment(text):
    sentiment_analysis = pipeline('sentiment-analysis')
    result = sentiment_analysis(text)
    # print(result)
    # return result[0]['label']
    return result[0]

def tokenize_text(text):
    """Encodes text into a numerical representation."""
    inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
    outputs = model(**inputs)
    embeddings = outputs.pooler_output.detach().numpy() 
    
    return embeddings

def smart_search(query, data, top_k=5):
    """Performs semantic search based on the query and data."""
    query_embedding = tokenize_text(query)

    # Calculate cosine similarity between query and data embeddings
    scores = []
    for item in data:
        item_embedding = tokenize_text(item['text']) # Replace 'text' with the actual field name
        score = cosine_similarity(query_embedding, item_embedding)[0][0]
        scores.append((item, score))

    # Sort results by score in descending order
    scores.sort(key=lambda x: x[1], reverse=True)

    # Return top k results
    return [result[0] for result in scores[:top_k]]

def smart_search_product(query, top_k=5):
    data = []
    for product in Product.objects.all():
        # {'text': 'The Eiffel Tower is a famous landmark in Paris.'},
        data.append({'text': product.description, 'product_id': product.id})

    results = smart_search(query, data, top_k)
    # for result in results:
    #     print(result['text'])
    #     print(result['product_id'])

    return results
