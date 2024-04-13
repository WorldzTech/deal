from django.conf.urls.static import static

from .chat_api import StartChat, SendMessage, GetChatHistory
from django.urls import path

urlpatterns = [
    path('chats/start/', StartChat.as_view(), name='api_chat_start'),
    path('chats/sendmessage/', SendMessage.as_view(), name='api_chat_sendmessage'),
    path('chats/', GetChatHistory.as_view(), name='api_chat_history'),
]
