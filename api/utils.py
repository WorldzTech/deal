from rest_framework.response import Response
from rest_framework.views import APIView

from storage.models import StorageUnit


class remdup(APIView):
    def post(self, request):
        units = list(StorageUnit.objects.all())
        rels = []
        ids = []

        for unit in units:
            if [unit.product.title, unit.size] not in rels:
                rels.append([unit.product.title, unit.size])
                ids.append(unit.id)

        all_ids = set([x.id for x in units])
        ids_to_delete = all_ids.difference(ids)

        for idc in ids_to_delete:
            StorageUnit.objects.get(id=idc).delete()

        return Response({
            'res': f'{len(units)} {len(rels)}',
            'ids': ids_to_delete
        })
