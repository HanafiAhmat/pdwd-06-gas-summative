import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Chat, ChatHistory
from .forms import ChatHistoryForm
from libs.commons import convert_markdown_to_html
from libs.genai import get_gemini_chatbot_response

def get_user_chat_histories(request):
    if request.user.is_authenticated:
        chat = Chat.objects.filter(user_id=request.user.id).first()
        if chat is None:
            chat = Chat.objects.filter(session_key=request.session.session_key).first()
            if chat is not None:
                chat.user_id = request.user.id
                chat.save()
            else:
                chat = Chat.objects.create(
                    user=request.user,
                    session_key=request.session.session_key
                )
    else:
        chat = Chat.objects.filter(session_key=request.session.session_key).first()
        if chat is None:
            chat = Chat.objects.create(session_key=request.session.session_key)

    chatHistories = chat.histories.all().order_by('timestamp')

    return chat, chatHistories

@csrf_protect
def retrieve_chat_history(request):
    chatHistories = [];
    if request.method == "POST":
        chat, chatHistories = get_user_chat_histories(request)
        chatHistories = serialize("json", chatHistories)
        chatHistories = json.loads(chatHistories)

    return JsonResponse({'chatHistories': chatHistories}, status=200)

@csrf_protect
def add_chat_message(request):
    bot_response = ''
    if request.method == "POST":
        postData = json.loads(request.body)
        user_message = postData.get('user_message', '')
        if user_message != '':
            chat, chatHistories = get_user_chat_histories(request)
            bot_response = convert_markdown_to_html(get_gemini_chatbot_response(user_message, chatHistories))
            ChatHistory.objects.create(
                chat=chat,
                user_message=user_message,
                bot_response=bot_response
            )

    return JsonResponse({'result': bot_response}, status=200)
