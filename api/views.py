import json
import logging
import math

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.backends.base.base import logger
from django.db.models import Q
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Product, ProductTag, ProductShowcase, OrderInvoice, EditableImage

from core.serializer import *
from deal.settings_prod import MAILSEND_TOKEN
from storage.models import StorageUnit
from mailersend import emails

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
            data['data']['photos'].sort(key=lambda x: x['id'])
            data['data']['rowtags'] = ','.join([x['name'] for x in ProductSerializer(product).data['tags']])
            data['ok'] = True
            if avail:
                availables = StorageUnit.objects.filter(product=product)
                data['available'] = []
                for available in availables:
                    av = {"size": available.size, "amount": available.amount, "storageUnitId": available.id}
                    if available.amount > 0:
                        data['available'].append(av)
        else:
            data['ok'] = False

        return Response(data)


class SearchProductByMask(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        mask = request.GET.get('mask')
        products = Product.objects.filter(Q(title__icontains=mask) | Q(title__icontains=" ".join(mask.split()[::-1])))
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


class RemoveProductFromUserCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        item = request.data.get('item')
        size = request.data.get('size')

        request.user.cart[item][size]['amount'] -= 1

        if request.user.cart[item][size]['amount'] == 0:
            del request.user.cart[item][size]

        request.user.save()

        return Response(status=status.HTTP_200_OK)


class GetCatalog(APIView):
    def get(self, request):
        page = int(request.GET.get('page', 1))
        pagination_step = 20
        filter_tags_raw = request.GET.get('filters', None)
        minPrice = float(request.GET.get('minPrice', 0))
        maxPrice = float(request.GET.get('maxPrice', 10 ** 10))
        newest = request.GET.get('newest', False)

        if filter_tags_raw:
            filter_tags = filter_tags_raw.split(',')
            fl = {}
            for f in filter_tags:
                if 'size_' not in f:
                    f_obj = ProductTag.objects.filter(name=f).first()
                    f_sections = ProductTagGroup.objects.all()

                    f_section = None
                    for s in f_sections:
                        if f_obj in s.tags.all():
                            f_section = s

                    if f_section.name not in fl.keys():
                        fl[f_section.name] = []

                    fl[f_section.name].append(f)
        else:
            filter_tags = None

        catalog = Product.objects.all()

        logger.debug("FILTERS: " + str(filter_tags))

        # if filter_tags:
        #     for f_section in fl.keys():
        #         filters = set(fl[f_section])
        #         new_catalog = []
        #         for product in catalog:
        #             products_tags = set([x.name for x in product.tags.all()])
        #             if len(list(products_tags.intersection(filters))) > 0:
        #                 new_catalog.append(product)
        #         catalog = new_catalog
        #
        #     sizes = [x.split('_')[1].replace('dot', '.').replace('slash', '/') for x in filter_tags if 'size_' in x]
        #
        #     if len(sizes) > 0:
        #         newCatalog = []
        #         for product in catalog:
        #             if StorageUnit.objects.filter(product=product, size__in=sizes, amount__gt=0).exists():
        #                 newCatalog.append(product)
        #
        #         catalog = newCatalog

        # SEX FILTERING
        newCatalog = []
        sex_filter_group = set([x.name for x in ProductTagGroup.objects.get(name="Пол").tags.all()])

        if filter_tags:
            inner_sex_filters = set(filter_tags).intersection(sex_filter_group)
            filter_tags = list(set(filter_tags).difference(inner_sex_filters))
            if len(inner_sex_filters) > 0:
                for product in catalog:
                    if len(set([x.name for x in product.tags.all()]).intersection(set(inner_sex_filters))) > 0:
                        newCatalog.append(product)

                catalog = newCatalog

        # BRAND FILTERING
        newCatalog = []
        brand_filter_group = set([x.name for x in ProductTagGroup.objects.get(name="Бренды").tags.all()])

        if filter_tags:
            inner_brand_filters = set(filter_tags).intersection(brand_filter_group)
            filter_tags = list(set(filter_tags).difference(inner_brand_filters))
            if len(inner_brand_filters) > 0:
                for product in catalog:
                    if len(set([x.name for x in product.tags.all()]).intersection(set(inner_brand_filters))) > 0:
                        newCatalog.append(product)

                catalog = newCatalog

        newCatalog = []
        if filter_tags:
            for product in catalog:
                if len(set([x.name for x in product.tags.all()]).intersection(set(filter_tags))) > 0:
                    newCatalog.append(product)

            catalog = newCatalog

        newCatalog = []
        for product in catalog:
            if minPrice <= product.price <= maxPrice:
                newCatalog.append(product)

        catalog = newCatalog

        data = []

        total_pages = math.ceil(len(catalog) / pagination_step)

        catalog.sort(key=lambda x: x.id, reverse=True)

        if page != -1:
            for product in catalog[(page - 1) * pagination_step:page * pagination_step]:
                data.append(ProductSerializer(product).data)
        else:
            for product in catalog:
                data.append(ProductSerializer(product).data)

        for d in data:
            d['photos'].sort(key=lambda x: x['id'])

        if page != -1:
            return Response(data={"page": page, "pages": total_pages, "total": len(catalog), "catalog": data, "filters": filter_tags},
                            status=status.HTTP_200_OK)
        else:
            return Response(data, status=status.HTTP_200_OK)


class TagGroupsEndpoint(APIView):
    def get(self, request):
        gid = request.GET.get('id')
        withIds = request.GET.get('wid', False)

        gname = request.GET.get('gname', None)

        if gname:
            if ProductTagGroup.objects.filter(name=gname).exists():
                gid = ProductTagGroup.objects.get(name=gname).id

        if gid:
            data = {}
            tagGroups = ProductTagGroup.objects.all()
            for tagGroup in tagGroups:
                if int(gid) == tagGroup.id:
                    data[tagGroup.name] = {}
                    for tag in tagGroup.tags.all():
                        data[tagGroup.name][tag.name.capitalize()] = tag.name
        else:
            data = {}
            tagGroups = ProductTagGroup.objects.all()
            for tagGroup in tagGroups:
                if withIds:
                    data[tagGroup.name] = {'id': tagGroup.id, 'body': {}}
                else:
                    data[tagGroup.name] = {}
                for tag in tagGroup.tags.all():
                    if withIds:
                        data[tagGroup.name]['body'][tag.name.capitalize()] = tag.name
                    else:
                        data[tagGroup.name][tag.name.capitalize().replace('_', ' ')] = tag.name
        return Response(data)

    def post(self, request):
        name = request.data.get('groupName', None)
        if name and not ProductTagGroup.objects.filter(name=name).exists() and len(name.strip()) > 0:
            ProductTagGroup.objects.create(name=name)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        gid = request.GET.get('gid', None)
        print(gid)

        ProductTagGroup.objects.get(id=gid).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsEndpoint(APIView):
    def get(self, request):
        tags = ProductTag.objects.all()
        data = []
        for tag in tags:
            data.append({'id': tag.id, 'name': tag.name})
        return Response(data)

    def post(self, request):
        tagName = request.data.get('tagName').strip().lower().replace(' ', '_')
        if len(tagName) == 0 or ProductTag.objects.filter(name=tagName).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ProductTag.objects.create(name=tagName)
        return Response(status=status.HTTP_201_CREATED)


class TagDeleteEndpoint(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        tagName = request.data['tagName']

        tag = ProductTag.objects.get(name=tagName)
        tag.delete()

        return Response(status=status.HTTP_200_OK)


class ShowcaseEndpoint(APIView):
    def get(self, request):
        sid = request.GET.get('sid', None)

        showcase = ProductShowcase.objects.filter(id=sid).first()

        if showcase:
            return Response(showcase.take_items())
        else:
            showcases = ProductShowcase.objects.all()

            data = []
            for showcase in showcases:
                data.append(ShowcaseSerializer(showcase).data)

            return Response(data)


class SwitchShowcaseProductEndpoint(APIView):
    def post(self, request):
        showcaseId = request.data.get('sid', None)
        productId = request.data.get('pid', None)

        showcase = ProductShowcase.objects.filter(id=showcaseId).first()
        product = Product.objects.filter(id=productId).first()

        if product in showcase.products.all():
            showcase.products.remove(product)
        else:
            showcase.products.add(product)

        return Response(status=status.HTTP_200_OK)


class GetAvailableSizes(APIView):
    def get(self, request):
        sizes = list(set([x.size for x in StorageUnit.objects.all()]))

        return Response(sizes)


class GeneratePaymentLink(APIView):
    def post(self, request):
        cid = request.GET.get('cid', None)

        cartData = request.data['cart']
        address = request.data['address']
        mobilePhone = request.data['mobilePhone']
        fullname = request.data['fullname']
        email = request.data['email']

        client = None

        try:
            client = UserModel.objects.get(id=cid)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        invoice = OrderInvoice.objects.create(
            client=client,
            address=address,
            mobile_phone=mobilePhone,
            full_name=fullname,
            email=email,
        )

        return Response({"link": invoice.get_payment_link()}, status=status.HTTP_200_OK)


class PaymentsNotify(APIView):
    def post(self, request):
        print("GET POST NOTIFY")
        print(request.data)

        logger = logging.getLogger(__name__)
        logger.debug("GET POST NOTIFY")
        logger.debug(request.data)

        invoiceId = request.data['service_name']

        invoice = OrderInvoice.objects.get(invoiceId=invoiceId)

        invoice.apply_invoice()

        return Response(status=status.HTTP_200_OK)


class GetEditableImage(APIView):
    def get(self, request):
        ei_id = request.GET.get('eid', None)

        if ei_id:
            ei: EditableImage = EditableImage.objects.filter(id=ei_id).first()

            if ei:
                return Response({"url": ei.get_url()}, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class NewsSubscribe(APIView):
    def post(self, request):
        email = request.data['email']

        try:
            # assigning NewEmail() without params defaults to MAILERSEND_API_KEY env var
            mailer = emails.NewEmail(MAILSEND_TOKEN)

            # define an empty dict to populate with mail values
            mail_body = {}

            mail_from = {
                "name": "Deal News Notificator",
                "email": "MS_c91A0W@trial-2p0347z5zr9lzdrn.mlsender.net",
            }

            recipients = [
                {
                    "name": "Deal Admin",
                    "email": "felix.trof@gmail.com",
                }
            ]

            reply_to = {
                "name": "noreply",
                "email": "noreply@domain.com",
            }

            mailer.set_mail_from(mail_from, mail_body)
            mailer.set_mail_to(recipients, mail_body)
            mailer.set_subject("Hello!", mail_body)
            mailer.set_html_content("This is the HTML content", mail_body)
            mailer.set_plaintext_content("This is the text content", mail_body)
            mailer.set_reply_to(reply_to, mail_body)

            # using print() will also return status code and data
            mailer.send(mail_body)
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'err': e}, status=status.HTTP_400_BAD_REQUEST)