from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import UserSerializer
from users.models import DealUser


class GetAllUsers(APIView):
    def get(self, request):
        users = DealUser.objects.all()

        resp = [UserSerializer(x).data for x in users]

        return Response(resp, status=status.HTTP_200_OK)

