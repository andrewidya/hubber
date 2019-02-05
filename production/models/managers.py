from django.db import models


class InventoryItemsManager(models.Manager):
    def get_queryset(self):
        stocklevel_quantity = models.Sum('stocklevel__quantity', distinct=True)
        productusage_quantity = models.Sum('productusage__quantity', distinct=True)
        manufacture_quantity = models.Sum('billofmaterial__manufacture__quantity', distinct=True)

        return super().get_queryset().annotate(stock=stocklevel_quantity, usage=productusage_quantity,
                                               produce=manufacture_quantity)