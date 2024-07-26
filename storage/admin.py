from django.contrib import admin

from storage.models import StorageUnit


class StorageUnitAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'amount')


# Register your models here.
admin.site.register(StorageUnit, StorageUnitAdmin)
