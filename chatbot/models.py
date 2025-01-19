from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, null=True, related_name="chat")
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chats'

class ChatHistory(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="histories")
    user_message = models.TextField()
    bot_response = models.TextField(default=None, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_histories'
        ordering = ["timestamp"]
