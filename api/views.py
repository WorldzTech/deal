import json

from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Product

from core.serializer import *
from storage.models import StorageUnit


# Create your views here.
class GetBlogPost(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        post_id = request.GET.get('id')
        data = {}
        if BlogPost.objects.filter(id=post_id).exists():
            blogpost = BlogPost.objects.get(id=post_id)
            data['data'] = BlogPostSerializer(blogpost).data
            data['ok'] = True
        else:
            data['ok'] = False

        return Response(data)


class GetProduct(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        product_item = request.GET.get('item')
        avail = request.GET.get('avail')
        data = {}
        if Product.objects.filter(item=product_item).exists():
            product = Product.objects.get(item=product_item)
            data['data'] = ProductSerializer(product).data
            data['ok'] = True
            if avail:
                availables = StorageUnit.objects.filter(product=product)
                data['available'] = {}
                for available in availables:
                    if available.amount > 0:
                        data['available'][available.size] = available.amount
        else:
            data['ok'] = False

        return Response(data)


class SearchProductByMask(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        mask = request.GET.get('mask')
        products = Product.objects.filter(title__icontains=mask)
        data = {
            'mask': mask,
            'res': [],
            'count': len(products)
        }
        for product in products:
            data['res'].append(ProductSerializer(product).data)

        return Response(data)


class AddProductToCart(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        productItem = request.data.get('productItem')
        productSize = request.data.get('productSize')
        user = request.user

        cart = request.user.cart

        if Product.objects.filter(item=productItem).exists():
            product = Product.objects.get(item=productItem)
            if StorageUnit.objects.filter(product=product, size=productSize).exists():
                storageUnit = StorageUnit.objects.get(product=product, size=productSize)
                amount = 0
                if productItem in cart.keys():
                    if productSize in cart[productItem].keys():
                        amount = cart[productItem][productSize]['amount']
                if storageUnit.amount >= amount + 1:
                    if product.item not in cart.keys():
                        cart[product.item] = {}
                    if storageUnit.size not in cart[product.item].keys():
                        cart[product.item][storageUnit.size] = {
                            'amount': 1,
                            'price': product.price,
                            'totalPrice': product.price
                        }
                    else:
                        cart[product.item][storageUnit.size]['amount'] += 1
                        cart[product.item][storageUnit.size]['totalPrice'] += product.price

                    request.user.cart = cart
                    request.user.save()
                    return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)