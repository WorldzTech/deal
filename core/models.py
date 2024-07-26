import base64
import random
import string
import uuid
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.sites import requests
from django.db import models
import chats.utils as chatsUtils
from chats.models import Chat

import requests

from core.utils import create_order

UserModel = get_user_model()


# Create your models here.
class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    shortDescription = models.TextField(blank=True, null=True)
    content = models.TextField()
    cover = models.ImageField(upload_to='covers/')


class ProductPhoto(models.Model):
    image = models.ImageField(upload_to='products/')


class ProductTagGroup(models.Model):
    name = models.CharField(max_length=255)
    tags = models.ManyToManyField('ProductTag')


class ProductTag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    class ProductSex(models.TextChoices):
        male = 'Мужское'
        female = 'Женское'

    title = models.CharField(max_length=255)
    item = models.CharField(max_length=8)
    shortDescription = models.TextField(blank=True, null=True)
    description = models.TextField()
    price = models.FloatField()
    photos = models.ManyToManyField(ProductPhoto)

    sex = models.CharField(choices=ProductSex, max_length=20, null=True, blank=True)
    tags = models.ManyToManyField(ProductTag, blank=True, null=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        created = "created", "Created"
        paid = "paid", "Paid"
        delivered = "delivered", "Delivered"
        cancelled = "cancelled", "Cancelled"
        delivering = "delivering", "Delivering"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    supportChat = models.ForeignKey(Chat, on_delete=models.PROTECT, null=True)

    innerId = models.CharField(max_length=7, null=True, blank=True)

    creation_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(choices=OrderStatus, max_length=20)

    products = models.JSONField(null=True, blank=True)

    totalPrice = models.FloatField(null=True, blank=True)

    email = models.EmailField(blank=True, null=True, max_length=254)
    address = models.TextField(null=True, blank=True)
    receiverFullname = models.CharField(max_length=100, null=True, blank=True)
    phoneNumber = models.CharField(max_length=12, null=True, blank=True)

    def create_support_chat(self):
        admin = UserModel.objects.get(mobilePhone='+71234')
        chat = chatsUtils.start_chat(byUser=self.user, toUser=admin,
                                     title="Заказ №" + self.innerId)
        chat.add_message(who=admin,
                         content=f'Здравствуйте! Ваш заказ №{self.innerId} создан! Мы обработаем его и запланируем дату доставки. Спасибо.')
        self.supportChat = chat
        self.save()

    def generate_inner_id(self):
        abc = string.digits
        p1 = ''.join(random.choices(abc, k=3))
        p2 = ''.join(random.choices(abc, k=3))
        print([p1, p2])
        innerId = "-".join([p1, p2])
        while Order.objects.filter(innerId=innerId).exists():
            p1 = random.choices(abc, k=3)
            p2 = random.choices(abc, k=3)
            innerId = "-".join([p1, p2])

        self.innerId = innerId
        self.save()


class SupportRequest(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    topic = models.CharField(max_length=255)
    description = models.TextField()
    isActive = models.BooleanField(default=True)
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT, blank=True, null=True)

    def startChat(self):
        chat = chatsUtils.start_chat(byUser=self.user, toUser=UserModel.objects.get(mobilePhone='+71234'),
                                     title=self.topic)
        chat.add_message(who=self.user, content=self.description)
        self.chat = chat
        self.save()


class ProductShowcase(models.Model):
    name = models.CharField(max_length=255)
    products = models.ManyToManyField(Product)

    def __str__(self):
        return self.name

    def take_items(self):
        return [x.item for x in self.products.all()]


class OrderInvoice(models.Model):
    invoiceId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pay_amount = models.FloatField(null=True, blank=True)
    client = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    order_data = models.JSONField(null=True, blank=True, default={})
    address = models.CharField(max_length=255, default="")
    mobile_phone = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    applied = models.BooleanField(default=False)

    # cartData = request.data['cart']
    #         address = request.data['address']
    #         mobilePhone = request.data['mobilePhone']
    #         fullname = request.data['fullname']
    #         email = request.data['email']

    def apply_invoice(self):
        if self.applied:
            return

        order = create_order(self)

        order.generate_inner_id()

        order.create_support_chat()

        self.client.cart = {}
        self.client.save()

        self.applied = True
        self.save()

    def get_payment_link(self):
        self.order_data = self.client.cart

        cart = dict(self.order_data)
        items = cart.keys()

        totalPrice = 0

        for item in items:
            for size in dict(cart[item]):
                totalPrice += cart[item][size]['amount'] * cart[item][size]['price']

        self.pay_amount = totalPrice
        self.save()

        hashed = base64.b64encode(b'invoices:DealFashionInvoices')

        tokenResp = requests.get('https://deal-fashion.server.paykeeper.ru/info/settings/token/', headers={
            "Authorization": "Basic aW52b2ljZXM6RGVhbEZhc2hpb25JbnZvaWNlcw=="
        })

        tokenRes = tokenResp.json()
        token = tokenRes['token']

        payment_data = {
            "pay_amount": totalPrice,
            "clientId": self.client.id,
            "orderId": self.invoiceId,
            "service_name": str(self.invoiceId),
            "client_email": self.client.email,
            "client_phone": self.client.mobilePhone,
            "expiry": str((datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")),
            "token": token
        }

        resp = requests.post("https://deal-fashion.server.paykeeper.ru/change/invoice/preview/", data=payment_data,
                             headers={
                                 "Authorization": f"Basic aW52b2ljZXM6RGVhbEZhc2hpb25JbnZvaWNlcw=="
                             })
        res = resp.json()

        return res['invoice_url']
