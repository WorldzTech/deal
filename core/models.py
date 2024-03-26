from django.contrib.auth import get_user_model
from django.db import models

UserModel = get_user_model()

# Create your models here.
class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    shortDescription = models.TextField(blank=True, null=True)
    content = models.TextField()
    cover = models.ImageField(upload_to='covers/')


class ProductPhoto(models.Model):
    image = models.ImageField(upload_to='products/')


class Product(models.Model):
    title = models.CharField(max_length=255)
    item = models.CharField(max_length=8)
    shortDescription = models.TextField(blank=True, null=True)
    description = models.TextField()
    price = models.FloatField()
    photos = models.ManyToManyField(ProductPhoto)


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        created = "created", "Created"
        paid = "paid", "Paid"
        delivered = "delivered", "Delivered"
        cancelled = "cancelled", "Cancelled"
        delivering = "delivering", "Delivering"

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    creation_date = models.DateTimeField(auto_now_add=True)
    delivered_date = models.DateTimeField(blank=True, null=True)

    status = models.CharField(choices=OrderStatus, max_length=20)

    products = models.JSONField(null=True, blank=True)
