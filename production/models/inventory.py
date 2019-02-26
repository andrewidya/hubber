from decimal import Decimal

from django.utils.translation import  ugettext_lazy as _
from django.db import models

from production.models.customer import Supplier, Customer
from production.models.managers import InventoryItemsManager


class UnitMeasurement(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=45)

    class Meta:
        verbose_name = _("1.4. Unit Satuan")
        verbose_name_plural = _("1.4. Unit Satuan")
        app_label = 'production'

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('id__iexact', 'name__icontains')


class InventoryItems(models.Model):
    TYPE = (
        ('TTD', "Raw material"),
        ('BT', "Finished good"),
        ('CON', "Consumable"),
    )
    code = models.CharField(verbose_name=_("Code"), max_length=45, unique=True)
    name = models.CharField(verbose_name=_("Name"), max_length=45)
    type = models.CharField(verbose_name=_("Type"), max_length=3, choices=TYPE)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=2, max_digits=14)
    initial = models.DecimalField(verbose_name=_("Saldo Awal"), decimal_places=4, max_digits=14,
                                  default=0)
    objects = InventoryItemsManager()

    class Meta:
        verbose_name = _("1.5. Stock Barang")
        verbose_name_plural = _("1.5. Daftar Stock Barang")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.code, self.name)

    @staticmethod
    def autocomplete_search_fields():
        return ('id__iexact', 'code__icontains',)

    def purchased(self):
        agg_purchased = self.stocklevel_set.all().aggregate(total=models.Sum('quantity'))
        val = agg_purchased.get('total') or Decimal(0.0000)
        return round(val, 4)

    def produced(self):
        agg_produced = self.billofmaterial_set.filter(manufacture__status='done').aggregate(total=models.Sum('manufacture__quantity'))
        val = agg_produced.get('total') or Decimal(0.0000)
        return round(val, 4)

    def used(self):
        agg_used = self.productusage_set.all().aggregate(total=models.Sum('quantity'))
        val = agg_used.get('total') or Decimal(0.0000)
        return round(val, 4)

    def delivered(self):
        agg_delivered = self.stockmovement_set.all().aggregate(total=models.Sum('quantity'))
        val = agg_delivered.get('total') or Decimal(0.0000)
        return round(val, 4)

    def adjustment(self):
        agg_adjust = self.inventoryadjustment_set.all().aggregate(total=models.Sum('quantity'))
        val = agg_adjust.get('total') or Decimal(0.0000)
        return round(val, 4)

    def availability(self):
        initial = self.initial
        purchased = self.purchased()
        produced = self.produced()
        used = self.used()
        delivered = self.delivered()
        ajdustment = self.adjustment()

        avl = self.initial + self.purchased() + self.produced() - self.used() - self.delivered() + self.adjustment()
        return round(avl, 4)


class StockLevel(models.Model):
    STATUS = (
        ('receipt', "Receipt"),
        ('return', "Return")
    )
    item = models.ForeignKey(InventoryItems, verbose_name=_("Item"), on_delete=models.CASCADE)
    delivery_note = models.CharField(verbose_name=_("Delivery note"), max_length=45, null=True,
                                     blank=True)
    datetime = models.DateTimeField(verbose_name=_("Datetime"))
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.CASCADE)
    status = models.CharField(verbose_name=_("Status"), max_length=7, choices=STATUS)
    supplier = models.ForeignKey(Supplier, verbose_name=_("Supplier"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("1.6. Pembelian Barang")
        verbose_name_plural = _("1.6. Pembelian Barang")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.delivery_note, self.item.name)

    def item_type(self):
        return self.item.type
    item_type.short_description = "Type"


class StockMovement(models.Model):
    STATUS = (
        ('sent', "Delivery"),
        ('return', "Return")
    )
    delivery_order = models.CharField(verbose_name=_("Delivery order"), max_length=45, null=True, blank=True)
    datetime = models.DateTimeField(verbose_name=_("Datetime"))
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    item = models.ForeignKey(InventoryItems, verbose_name=_("Item"), on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.CASCADE)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.CASCADE)
    status = models.CharField(verbose_name=_("Status"), max_length=6, choices=STATUS)
    jo_number = models.CharField(verbose_name=_("JO number"), max_length=50, null=True, blank=True)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        verbose_name = _("1.7. Pengiriman Barang [ Finished Good ]")
        verbose_name_plural = _("1.7. Pengiriman Barang [ Finisehd Good ]")
        app_label = 'production'

    def __str__(self):
        return "{} - {} - {}".format(self.delivery_order, self.customer.name, self.item.name)


class InventoryAdjustment(models.Model):
    item = models.ForeignKey(InventoryItems, verbose_name=_("Item"), on_delete=models.CASCADE)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14,
                                   default=0)
    last_edited = models.DateTimeField(verbose_name=_("Last edited"), auto_now=True)
    first_created = models.DateTimeField(verbose_name=_("First edited"), auto_now_add=True)

    class Meta:
        verbose_name = _("2.1. Penyesuaian / Pemutihan Stock")
        verbose_name_plural = _("2.1. Penyesuaian / Pemutihan Stock")
        app_label = 'production'

    def __str__(self):
        return self.item.name
