from django.utils.translation import  ugettext_lazy as _
from django.db import models

# Create your models here.
class Customer(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=45)

    class Meta:
        verbose_name = _("1.1. Customer")
        verbose_name_plural = _("1.1. Daftar Customer")
        app_label = 'production'

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('id__iexact', 'name__icontains')


class CustomerCategory(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=45)

    class Meta:
        verbose_name = _("1.2. Kategori Customer")
        verbose_name_plural = _("1.2. Daftar Kategori Customer")
        app_label = 'production'

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('id__iexact', 'name__icontains')


class Supplier(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=45)

    class Meta:
        verbose_name = _("1.3. Supplier")
        verbose_name_plural = _("1.3. Daftar Supplier")
        app_label = 'production'

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ('id__iexact', 'name__icontains')
