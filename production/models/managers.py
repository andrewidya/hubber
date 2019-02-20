from django.db import models


class InventoryItemsManager(models.Manager):
    def get_queryset(self):
        stocklevel_quantity = models.Sum('stocklevel__quantity', distinct=True)
        productusage_quantity = models.Sum(
            'productusage__quantity',
            filter=models.Q(productusage__manufacture__status='done'),
            distinct=True
        )
        manufacture_quantity = models.Sum('billofmaterial__manufacture__quantity', distinct=True)
        deliver_quantity = models.Sum('stockmovement__quantity')
        adjustment = models.Sum('inventoryadjustment__quantity', distinct=True)

        return super().get_queryset().annotate(stock=stocklevel_quantity, usage=productusage_quantity,
                                               produce=manufacture_quantity, deliver=deliver_quantity,
                                               adjustment=adjustment)
