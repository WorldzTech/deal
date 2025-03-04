from rest_framework import serializers

from users.models import DealUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DealUser
        fields = '__all__'