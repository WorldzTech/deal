from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Chat
from chats.serializers import ChatSerializer

UserModel = get_user_model()


class StartChat(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        chat = Chat.objects.create(p1=user, p2=UserModel.objects.get(mobilePhone='+71234'))

        return Response(status=status.HTTP_201_CREATED)


class SendMessage(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        chatId = request.data['chatId']
        content = request.data['content']

        chat = Chat.objects.filter(id=chatId).first()

        if chat:
            if chat.add_message(who=user, content=content):
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetChatHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        chatId = request.GET.get('chatId')

        chat = Chat.objects.filter(id=chatId).first()

        if chat:
            return Response(ChatSerializer(chat).data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
