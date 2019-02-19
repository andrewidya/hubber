from decimal import Decimal

from django.dispatch import receiver
from django.db.models.signals import post_save

from production.models.inventory import InventoryItems, StockMovement, StockLevel
from production.models.manufacture import ProductUsage, Manufacture


def get_total_stock_level(obj):
    stock = obj.stock or Decimal(0.000)
    usage = obj.usage or Decimal(0.000)
    deliver = obj.deliver or Decimal(0.000)
    produce = obj.produce or Decimal(0.000)
    adjustment = obj.adjustment or Decimal(0.000)
    balance = obj.initial or Decimal(0.0000)
    total = (balance + stock + produce + adjustment) - usage - deliver
    obj.available = total
    obj.save()


@receiver(post_save, sender=StockLevel)
def receipt_update(sender, instance, created, **kwargs):
    item = InventoryItems.objects.get(pk=instance.item.pk)
    get_total_stock_level(item)


@receiver(post_save, sender=StockMovement)
def delivery_update(sender, instance, created, **kwargs):
    item = InventoryItems.objects.get(pk=instance.item.pk)
    get_total_stock_level(item)


@receiver(post_save, sender=ProductUsage)
def productusage_update(sender, instance, created, **kwargs):
    item = InventoryItems.objects.get(pk=instance.item.pk)
    get_total_stock_level(item)


@receiver(post_save, sender=Manufacture)
def manufacture_update(sender, instance, created, **kwargs):
    item = InventoryItems.objects.get(pk=instance.bill_of_material.product.pk)
    get_total_stock_level(item)
