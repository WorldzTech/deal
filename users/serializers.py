from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.models import DealUser

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ['mobilePhone', 'firstname', 'password', 'email']

    def create(self, clean_data):
        user = UserModel.objects.create_user(mobilePhone=clean_data['mobilePhone'], email=clean_data['email'], firstname=clean_data['firstname'],  password=clean_data['password'])
        user.save()


class UserSigninSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def check_user(self, clean_data):
        user = authenticate(phoneNumber=clean_data['email'], password=clean_data['password'])
        if not user:
            raise ValidationError('Invalid credentials')
        return user