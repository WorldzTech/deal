import random
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Chat
from core.models import ProductPhoto, ProductTag, Product, SupportRequest
from core.forms import EditProductForm
from core.serializer import SupportRequestSerializer, DetailedSupportRequestSerializer

UserModel = get_user_model()


class ProductEndpoint(APIView):
    def post(self, request):
        name = request.data['name']
        price = int(request.data['price'])
        cover = request.data['cover']
        description = request.data['description']
        short_description = request.data['shortDescription']
        tags = request.data['tags']

        image = ProductPhoto.objects.create(image=cover)
        tagsList = []

        for tag in tags.split(','):
            tagObj = ProductTag.objects.filter(name=tag).first()
            if not tagObj:
                tagObj = ProductTag.objects.create(name=tag)
            tagsList.append(tagObj)

        item = ''.join([random.choice(string.digits) for x in range(8)])
        while Product.objects.filter(item=item).exists():
            item = ''.join([random.choice(string.digits) for x in range(8)])

        product = Product.objects.create(title=name, item=item, price=price, shortDescription=short_description,
                                         description=description)

        product.photos.add(image)

        for tag in tagsList:
            product.tags.add(tag)

        product.save()

        return Response({'item': item}, status=status.HTTP_201_CREATED)

    def put(self, request):
        name = request.data.get('name', None)
        price = request.data.get('price', None)
        description = request.data.get('description', None)
        short_description = request.data.get('shortDescription', None)
        tags = request.data.get('tags', None)
        cover = request.data.get('cover', None)
        productItem = request.data['productItem']

        product = Product.objects.get(item=productItem)

        if name:
            product.title = name

        if price:
            product.price = float(price)

        if description:
            product.description = description

        if short_description:
            product.shortDescription = short_description

        if tags:
            product.tags.clear()
            tagsList = []

            for tag in tags.split(','):
                tagObj = ProductTag.objects.filter(name=tag).first()
                if not tagObj:
                    tagObj = ProductTag.objects.create(name=tag)
                tagsList.append(tagObj)

                for tag in tagsList:
                    product.tags.add(tag)

        if cover:
            image = ProductPhoto.objects.create(image=cover)
            product.photos.clear()
            product.photos.add(image)

        product.save()

        return Response(status=status.HTTP_200_OK)


class SupportRequestsEndpoint(APIView):
    def get(self, request):
        supportRequests = SupportRequest.objects.all()
        response_data = []
        for request in supportRequests:
            response_data.append(SupportRequestSerializer(request).data)
        return Response(response_data)


class SupportRequestDetailsEndpoint(APIView):
    def get(self, request):
        support_request = SupportRequest.objects.filter(id=request.GET.get('id')).first()
        return Response(DetailedSupportRequestSerializer(support_request).data)


class SendMessageViaSupportAccountEndpoint(APIView):
    def get(self, request):
        chatId = request.GET.get('cid')
        message = request.GET.get('message')

        chat = Chat.objects.filter(id=chatId).first()
        admin = UserModel.objects.get(mobilePhone='1234')
        chat.add_message(admin, message)

        return Response(status=status.HTTP_200_OK)


class CloseSupportRequestEndpoint(APIView):
    def post(self, request):
        id = request.data['cid']
        support_request: SupportRequest = SupportRequest.objects.filter(id=id).first()
        support_request.isActive = False
        support_request.chat.add_message(support_request.chat.p2,
                                         'Ваше обращение закрыто, как и этот чат. Спасибо за обращение.')

        support_request.save()

        return Response(status=status.HTTP_200_OK)


class GetProductModelFields(APIView):
    def get(self, request):
        fields = {}
        for k in EditProductForm.__dict__['base_fields'].keys():
            fields[k] = str(EditProductForm.__dict__['base_fields'][k])
        return Response({"html": EditProductForm().__html__()})
