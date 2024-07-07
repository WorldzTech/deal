import random
import string

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chats.models import Chat
from core.models import ProductPhoto, ProductTag, Product, SupportRequest, ProductTagGroup, Order
from core.forms import EditProductForm
from core.serializer import SupportRequestSerializer, DetailedSupportRequestSerializer, OrderSerializer
from storage.models import StorageUnit
from storage.serializers import StorageSerializer, DetailedStorageUnitSerializer

UserModel = get_user_model()


class ProductEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        print(request.data)

        name = request.data['name']
        price = int(request.data['price'])
        cover = request.data['photos[]']
        description = request.data['description']
        short_description = request.data['shortDescription']
        tags = request.data['tags']

        print(cover)
        print(cover)
        print(cover)

        tagsList = []

        for tag in tags.split(','):
            tagName = tag.strip().lower().replace(' ', '_')
            if len(tagName) == 0 or ProductTag.objects.filter(name=tagName).exists():
                tagsList.append(ProductTag.objects.filter(name=tagName).first())

        item = ''.join([random.choice(string.digits) for x in range(8)])
        while Product.objects.filter(item=item).exists():
            item = ''.join([random.choice(string.digits) for x in range(8)])

        product = Product.objects.create(title=name, item=item, price=price, shortDescription=short_description,
                                         description=description)

        for f in request.FILES.getlist('photos[]'):
            image = ProductPhoto.objects.create(image=f)
            product.photos.add(image)

        for tag in tagsList:
            product.tags.add(tag)

        product.save()

        return Response({'item': item}, status=status.HTTP_201_CREATED)

    def put(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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

        print(request.FILES.getlist('photos[]'))
        if len(request.FILES.getlist('photos[]')) > 0:
            product.photos.clear()
            for f in request.FILES.getlist('photos[]'):
                image = ProductPhoto.objects.create(image=f)
                product.photos.add(image)

        product.save()

        return Response({'ph': request.FILES.getlist('photos[]'), 'raw': request.data, 'rph': request.data('photos')}, status=status.HTTP_200_OK)

    def delete(self, request):
        if not request.user.is_staff:
            print('//')
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        item = request.GET.get('item')

        product = Product.objects.get(item=item)

        product.delete()

        return Response(status=status.HTTP_200_OK)


class SupportRequestsEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        supportRequests = SupportRequest.objects.all()
        response_data = []
        for requestC in supportRequests:
            response_data.append(SupportRequestSerializer(requestC).data)

        sortBy = request.GET.get('sort', None)

        if sortBy:
            sortData = sortBy.split('_')
            if sortData[0] == 'date':
                response_data.sort(key=lambda x: x['date'])

                if sortData[1] == 'inc':
                    response_data = response_data[::-1]
            elif sortData[0] == 'status':
                response_data.sort(key=lambda x: x['isActive'])

                if sortData[1] == 'inc':
                    response_data = response_data[::-1]

        return Response(response_data)


class SupportRequestDetailsEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        support_request = SupportRequest.objects.filter(id=request.GET.get('id')).first()

        return Response(DetailedSupportRequestSerializer(support_request).data)


class SendMessageViaSupportAccountEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        chatId = request.GET.get('cid')
        message = request.GET.get('message')

        chat = Chat.objects.filter(id=chatId).first()
        admin = UserModel.objects.get(mobilePhone='+71234')
        chat.add_message(admin, message)

        return Response(status=status.HTTP_200_OK)


class CloseSupportRequestEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        id = request.data['cid']
        support_request: SupportRequest = SupportRequest.objects.filter(id=id).first()
        support_request.isActive = False
        support_request.chat.add_message(support_request.chat.p2,
                                         'Ваше обращение закрыто, как и этот чат. Спасибо за обращение.')

        support_request.save()

        return Response(status=status.HTTP_200_OK)


class GetProductModelFields(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        fields = {}
        for k in EditProductForm.__dict__['base_fields'].keys():
            fields[k] = str(EditProductForm.__dict__['base_fields'][k])
        return Response({"html": EditProductForm().__html__()})


class SwitchTagGroupsEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        tagId = request.data['tagId']
        groupId = request.data['groupId']

        tagsGroup = ProductTagGroup.objects.filter(id=groupId).first()
        tag = ProductTag.objects.get(id=tagId)

        if tag in tagsGroup.tags.all():
            tagsGroup.tags.remove(tag)
        else:
            tagsGroup.tags.add(tag)

        return Response(status=status.HTTP_200_OK)


class GetOrdersEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        oid = request.GET.get('oid', None)

        if oid:
            order = Order.objects.filter(id=oid).first()
            return Response(OrderSerializer(order).data)
        else:
            orders = Order.objects.all()
            response_data = []
            for order in orders:
                response_data.append(OrderSerializer(order).data)
            return Response(response_data)


class StorageEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        data = {}

        for storageUnit in StorageUnit.objects.all():
            if storageUnit.product.title not in data.keys():
                data[storageUnit.product.title] = {
                    'sizes': [],
                    'item': storageUnit.product.item
                }

            data[storageUnit.product.title]['sizes'].append(storageUnit.size)

        return Response(data)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        itemOrTitle = request.data['iot']
        size = request.data['size']
        amount = request.data['amount']

        print(amount, itemOrTitle, size)

        if size:
            product = Product.objects.filter(item=itemOrTitle).first()
            if not product:
                product = Product.objects.filter(title=itemOrTitle).first()

            if product:
                storageUnit = StorageUnit.objects.filter(product=product, size=size).first()
                if not storageUnit:
                    storageUnit = StorageUnit.objects.create(product=product, size=size, amount=0)
                storageUnit.amount += int(amount)
                storageUnit.save()

                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class SetOrderStatusEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        oid = request.data['oid']
        st = request.data['status']

        order = Order.objects.filter(id=oid).first()

        if order:
            order.status = st
            order.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class StorageUnitDetailsEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        item = request.GET.get('item')

        product = Product.objects.get(item=item)

        storageUnits = StorageUnit.objects.filter(product=product)

        data = {
            'title': product.title,
            'storage': {}
        }

        for storageUnit in storageUnits:
            data['storage'][storageUnit.size] = storageUnit.amount

        return Response(data)


class StoragePositionRemoveEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        product_item = request.data['product_item']
        size_details = request.data.get('size_details', None)

        product = Product.objects.get(item=product_item)

        if size_details:
            storageUnit = StorageUnit.objects.get(product=product, size=size_details)
            storageUnit.delete()
        else:
            storageUnits = StorageUnit.objects.filter(product=product).all()
            for unit in storageUnits:
                unit.delete()

        return Response(status=status.HTTP_200_OK)


class StoragePositionAdjust(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        item = request.data['item']
        size = request.data['size']
        act = request.data['act']

        product = Product.objects.get(item=item)

        storageUnit = StorageUnit.objects.get(product=product, size=size)
        if act == 'remove':
            if storageUnit.amount > 0:
                storageUnit.amount -= 1
        else:
            storageUnit.amount += 1

        storageUnit.save()

        return Response(status=status.HTTP_200_OK)

    def delete(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        item = request.data['item']
        size = request.data['size']

        product = Product.objects.get(item=item)

        storageUnit = StorageUnit.objects.get(product=product, size=size)
        storageUnit.amount -= 1

        storageUnit.save()

        return Response(status=status.HTTP_200_OK)


class RemoveStorageUnit(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        item = request.data['item']
        size = request.data['size']

        product = Product.objects.get(item=item)
        storageUnit = StorageUnit.objects.get(product=product, size=size)

        storageUnit.delete()

        return Response(status=status.HTTP_200_OK)


class MoveProductPhoto(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        item = request.data['item']
        photoId = request.data['photoId']
        direction = request.data['direction']

        product = Product.objects.get(item=item)
        photo = ProductPhoto.objects.get(id=photoId)

        photosList = list(product.photos.all())
        photosList.sort(key=lambda x: x.id)
        if direction == 'start':
            if photosList.index(photo) > 0:
                prevTmp = photosList[photosList.index(photo) - 1].image
                photosList[photosList.index(photo) - 1].image = photo.image
                photosList[photosList.index(photo) - 1].save()
                photo.image = prevTmp
                photo.save()
        else:
            if photosList.index(photo) < len(photosList)-1:
                prevTmp = photosList[photosList.index(photo) + 1].image
                photosList[photosList.index(photo) + 1].image = photo.image
                photosList[photosList.index(photo) + 1].save()
                photo.image = prevTmp
                photo.save()

        return Response(status=status.HTTP_200_OK)
