import random
import string

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import ProductPhoto, ProductTag, Product
from core.forms import EditProductForm


class CreateProduct(APIView):
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


class GetProductModelFields(APIView):
    def get(self, request):
        fields = {}
        for k in EditProductForm.__dict__['base_fields'].keys():
            fields[k] = str(EditProductForm.__dict__['base_fields'][k])
        return Response({"html": EditProductForm().__html__()})
