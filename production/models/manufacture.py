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
    price = models.DecimalField(verbose_name=_("Price"), max_digits=14, decimal_places=4)
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


class BillOfMaterialDetails(models.Model):
    bill_of_material = models.ForeignKey(BillOfMaterial, verbose_name=_("BoM"), on_delete=models.CASCADE)
    material = models.ForeignKey(InventoryItems, verbose_name=_("Material"), on_delete=models.CASCADE)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.CASCADE)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=4, max_digits=14)

    class Meta:
        verbose_name = _("1.9. Rincian Formula")
        verbose_name_plural = _("1.9. Daftar Rincian Formula")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.bill_of_material, self.material.name)


class Manufacture(models.Model):
    datetime = models.DateTimeField(verbose_name=_("Datetime"))
    bill_of_material = models.ForeignKey(BillOfMaterial, verbose_name=_("BoM"), on_delete=models.PROTECT)
    price = models.DecimalField(verbose_name=_("Price"), decimal_places=4, max_digits=14)
    customer = models.ForeignKey(Customer, verbose_name=_("Customer"), on_delete=models.PROTECT)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("2.0. Produksi")
        verbose_name_plural = _("2.0. Produksi")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.bill_of_material.code, self.customer.name)

    def _product_name(self):
        return self.bill_of_material.product.name


class ProductUsage(models.Model):
    item = models.ForeignKey(InventoryItems, verbose_name=_("Item"), on_delete=models.PROTECT)
    manufacture = models.ForeignKey(Manufacture, verbose_name=_("Manufacture process"),
                                    on_delete=models.CASCADE)
    quantity = models.DecimalField(verbose_name=_("Quantity"), decimal_places=4, max_digits=14)
    unit = models.ForeignKey(UnitMeasurement, verbose_name=_("Unit"), on_delete=models.PROTECT)

    class Meta:
        verbose_name = _("2.1. Penggunaan Barang")
        verbose_name_plural = _("2.1. Daftar Penggunaan Barang")
        app_label = 'production'

    def __str__(self):
        return "{} - {}".format(self.item.name, self.manufacture.bill_of_material.product.name)
