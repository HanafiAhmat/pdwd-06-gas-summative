from django.urls import path
from . import views

urlpatterns = [
    path('retrieve-history', views.retrieve_chat_history, name="chatbot_retrieve_history"),
    path('add-message', views.add_chat_message, name="chatbot_add_message"),
]
