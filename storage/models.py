from django.db import models

from core.models import Product


# Create your models here.
class StorageUnit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product')
    size = models.CharField(max_length=5)
    amount = models.IntegerField()
