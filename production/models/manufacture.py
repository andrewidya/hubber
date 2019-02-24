from decimal import Decimal

from django.utils.translation import  ugettext_lazy as _
from django.db import models

from production.models.customer import Customer, CustomerCategory
from production.models.inventory import InventoryItems, UnitMeasurement


class BillOfMaterial(models.Model):
    code = models.CharField(verbose_name=_("Code"), max_length=45)
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.CASCADE)
    customer_category = models.ForeignKey(CustomerCategory, verbose_name=_("Customer category"),
                                          on_delete=models.CASCADE)
    color_name = models.CharField(verbose_name=_("Color name"), max_length=45)
    product = models.ForeignKey(InventoryItems, verbose_name=_("Product"), on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_("Price"), max_digits=14, decimal_places=4, null=True,
                                blank=True, default=0)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        verbose_name = _("1.8. Formula")
        verbose_name_plural = _("1.8. Daftar Formula")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.code, self.product.name)

    @staticmethod
    def autocomplete_search_fields():
        return ('id__iexact', 'code__icontains')

    def output_weight(self):
        agg_val = self.billofmaterialdetails_set.all().aggregate(total=models.Sum('quantity'))
        val = agg_val.get('total') or Decimal(0.0000)
        return round(val, 4)


class BillOfMaterialDetails(models.Model):
    bill_of_material = models.ForeignKey(BillOfMaterial, verbose_name=_("BoM"), on_delete=models.CASCADE)
    material = models.ForeignKey(InventoryItems, verbose_name=_("Material"), on_delete=models.CASCADE)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=4, max_digits=14,
                                null=True, blank=True, default=0)

    class Meta:
        verbose_name = _("1.9. Rincian Formula")
        verbose_name_plural = _("1.9. Daftar Rincian Formula")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.bill_of_material, self.material.name)


class Manufacture(models.Model):
    STATUS = (
        ('on_going', 'Dalam proses'),
        ('pending', 'Pending'),
        ('done', 'Selesai'),
    )
    datetime = models.DateTimeField(verbose_name=_("Datetime"))
    bill_of_material = models.ForeignKey(BillOfMaterial, verbose_name=_("BoM"),on_delete=models.PROTECT)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=4, max_digits=14, default=0)
    bom_output_standard = models.DecimalField(
        verbose_name=_("Standard output formula"), decimal_places=4, max_digits=14, default=0,
        help_text=_("Jumlah output yang dikeluarkan oleh formula produksi, sesuai satuan dalam stock")
    )
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.PROTECT)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.PROTECT)
    status = models.CharField(verbose_name=_("Status"), max_length=8, choices=STATUS, default='pending')

    class Meta:
        verbose_name = _("1.9. Produksi")
        verbose_name_plural = _("1.9. Produksi")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.bill_of_material.code, self.customer.name)

    def save(self, *args, **kwargs):
        product_usages = self.productusage_set.all()
        total_price = 0
        if product_usages.exists():
            for i in product_usages:
                total_price += i.price
                i.save()
        self.price = total_price
        self.bom_output_standard = self.bill_of_material.output_weight()
        super().save(*args, **kwargs)

    def _product_name(self):
        return self.bill_of_material.product.name
    _product_name.short_description = _("Product name")


class ProductUsage(models.Model):
    item = models.ForeignKey(InventoryItems, verbose_name=_("Item"), on_delete=models.PROTECT)
    manufacture = models.ForeignKey(Manufacture, verbose_name=_("Manufacture process"),
                                    on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=4, max_digits=14, default=0)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("2.0. Penggunaan Barang")
        verbose_name_plural = _("2.0. Daftar Penggunaan Barang")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.item.name, self.manufacture.bill_of_material.product.name)

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.quantity * self.item.price
        super().save(*args, **kwargs)
