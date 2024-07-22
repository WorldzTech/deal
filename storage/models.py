from django.db import models

# Create your models here.
class StorageUnit(models.Model):
    product = models.ForeignKey("core.Product", on_delete=models.CASCADE, related_name='product')
    size = models.CharField(max_length=9)
    amount = models.IntegerField()
