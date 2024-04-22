import json

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Product, ProductTag

from core.serializer import *
from storage.models import StorageUnit

UserModel = get_user_model()


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
        userId = request.GET.get('uid', None)

        if userId and userId.isdigit():
            if UserModel.objects.filter(id=userId).exists():
                user = UserModel.objects.get(id=userId)
            else:
                user = None
        else:
            user = None

        product_item = request.GET.get('item')
        avail = request.GET.get('avail')
        data = {}
        if Product.objects.filter(item=product_item).exists():
            product = Product.objects.get(item=product_item)
            data['favorite'] = False

            if user:
                print("AUTHENTICATED")
                if user.favorites.filter(id=product.id).exists():
                    data['favorite'] = True
            else:
                print('NOT AUTHENTICATED')

            data['data'] = ProductSerializer(product).data
            data['data']['rowtags'] = ','.join([x['name'] for x in ProductSerializer(product).data['tags']])
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


class GetCatalog(APIView):
    def get(self, request):
        filter_tags_raw = request.GET.get('filters', None)
        minPrice = float(request.GET.get('minPrice', 0))
        maxPrice = float(request.GET.get('maxPrice', 10**10))

        if filter_tags_raw:
            filter_tags = filter_tags_raw.split(',')
            print("FILTERS APPLYING TAGS WITH", filter_tags)
        else:
            filter_tags = None
            print("NO FILTERS APPLYING")

        catalog = Product.objects.all()

        if filter_tags:
            for tagName in filter_tags:
                newCatalog = []
                print('FILTERING BY TAG', tagName)
                # catalog = catalog.filter(tags__name__in=[tagName])
                for product in catalog:
                    pt = [t.name for t in product.tags.all()]
                    if tagName in pt:
                        newCatalog.append(product)
                        print(f'{product} [{product.item}] passed with {pt}')
                    elif 'size_' in tagName:
                        newCatalog.append(product)
                catalog = newCatalog
                print(catalog)

            sizes = [x.split('_')[1] for x in filter_tags if 'size_' in x]


            if len(sizes) > 0:
                newCatalog = []
                print('FILTERING BY SIZE')
                print(sizes)
                for product in catalog:
                    if StorageUnit.objects.filter(product=product, size__in=sizes, amount__gt=0).exists():
                        newCatalog.append(product)

                catalog = newCatalog
                print(catalog)

        newCatalog = []
        for product in catalog:
            print(f"{minPrice} <= {product.price} <= {maxPrice}")
            if minPrice <= product.price <= maxPrice:
                newCatalog.append(product)

        catalog = newCatalog

        data = []
        for product in catalog:
            data.append(ProductSerializer(product).data)

        print(data)

        return Response(data=data, status=status.HTTP_200_OK)
