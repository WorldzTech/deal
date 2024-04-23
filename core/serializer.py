from rest_framework import serializers

from core.models import BlogPost, Product, Order, SupportRequest


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 2


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class SupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = '__all__'


class DetailedSupportRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportRequest
        fields = '__all__'
        depth = 3
