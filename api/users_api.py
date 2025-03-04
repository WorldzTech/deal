from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.serializers import UserSerializer
from users.models import DealUser


class GetAllUsers(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = DealUser.objects.all()

        resp = [UserSerializer(x).data for x in users]

        return Response(resp, status=status.HTTP_200_OK)

