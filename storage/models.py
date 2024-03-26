from django.db import models

from core.models import Product


# Create your models here.
class StorageUnit(models.Model):
    class ProductSize(models.TextChoices):
        XS = 'XS'
        S = 'S'
        M = 'M'
        L = 'L'
        XL = 'XL'
        XXL = 'XXL'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    size = models.CharField(max_length=3, choices=ProductSize)
    amount = models.IntegerField()
