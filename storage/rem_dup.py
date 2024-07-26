from storage.models import StorageUnit

units = StorageUnit.objects.all()
rels = set([[x.product, x.size] for x in units])

print(len(units), len(rels))