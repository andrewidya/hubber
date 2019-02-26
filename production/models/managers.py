from django.db import models


class InventoryItemsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            'stocklevel_set', 'billofmaterial_set', 'billofmaterial_set__manufacture_set',
            'productusage_set', 'stockmovement_set', 'inventoryadjustment_set'
        )
