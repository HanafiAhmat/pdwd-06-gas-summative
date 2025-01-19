from django import forms
from .models import ChatHistory

class ChatHistoryForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = ChatHistory
        fields = "__all__"
