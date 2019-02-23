from decimal import Decimal

from django.test import TransactionTestCase
from django.utils import timezone

from production.models.manufacture import Manufacture, BillOfMaterial, BillOfMaterialDetails
from production.models.inventory import Customer, UnitMeasurement, InventoryItems, StockMovement


def manufacture_data_creation(quantity):
    bom = BillOfMaterial.objects.get(code='BT-001')
    customer = Customer.objects.get(pk=1)
    unit = UnitMeasurement.objects.get(pk=1)
    manufacture = Manufacture.objects.create(
        datetime=timezone.now(),
        bill_of_material=bom,
        customer=customer,
        quantity=quantity,
        unit=unit,
        status='pending'
    )
    manufacture.save()


class ManufactureTest(TransactionTestCase):
    fixtures = [
        'unit_measurement.json', 'customer.json', 'customer_category.json',
        'inventory_items.json', 'bill_of_material.json', 'bill_of_material_detail.json'
    ]

    def setUp(self):
        manufacture_data_creation(Decimal(10.000))

    def test_pending_manufacture_stock(self):
        bom = BillOfMaterial.objects.get(code='BT-001')
        item = bom.product
        self.assertEqual(item.availability(), Decimal(0.0000))

    def test_on_going_manufacture_stock(self):
        bom = BillOfMaterial.objects.get(code='BT-001')
        item = bom.product
        self.assertEqual(item.availability(), Decimal(0.0000))

    def test_done_manufacture_stock(self):
        bom = BillOfMaterial.objects.get(code='BT-001')
        manufacture = Manufacture.objects.get(bill_of_material=bom)
        manufacture.status = 'done'
        manufacture.save()
        item = bom.product
        self.assertEqual(item.availability(), Decimal(10.0000))


class InventoryItemsTest(TransactionTestCase):
    fixtures = [
        'unit_measurement.json', 'customer.json', 'customer_category.json',
        'inventory_items.json', 'bill_of_material.json', 'bill_of_material_detail.json'
    ]

    def setUp(self):
        manufacture_data_creation(Decimal(20.000))

    def save_manufacture(self, quantity=Decimal(20.0000)):
        bom = BillOfMaterial.objects.get(code='BT-001')
        manufacture = Manufacture.objects.get(bill_of_material=bom)
        manufacture.status = 'done'
        manufacture.quantity = quantity
        manufacture.save()

    def deliver_product(self, item=None, quantity=None):
        unit = UnitMeasurement.objects.get(pk=1)
        customer = Customer.objects.get(pk=1)
        delivery = StockMovement.objects.create(
            datetime=timezone.now(),
            quantity=quantity,
            item=item,
            customer=customer,
            unit=unit,
            status='sent'
        )
        delivery.save()

    def return_product(self, item=None, quantity=None):
        unit = UnitMeasurement.objects.get(pk=1)
        customer = Customer.objects.get(pk=1)
        delivery = StockMovement.objects.create(
            datetime=timezone.now(),
            quantity=quantity * -1,
            item=item,
            customer=customer,
            unit=unit,
            status='return'
        )
        delivery.save()

    def test_item_stock_before_manufactured(self):
        item = InventoryItems.objects.get(code='BT-001')

        self.assertEqual(item.availability(), Decimal(0.0000))

    def test_item_stock_after_manufacture(self):
        self.save_manufacture(quantity=Decimal(20.0000))
        item = InventoryItems.objects.get(code='BT-001')
        self.assertEqual(item.availability(), Decimal(20.0000))

    def test_item_stock_after_delivered(self):
        self.save_manufacture(quantity=Decimal(20.0000))
        item = InventoryItems.objects.get(code='BT-001')
        self.deliver_product(item=item, quantity=Decimal(15.0000))
        self.assertEqual(item.availability(), Decimal(5.0000))

    def test_item_stock_after_returned(self):
        item = InventoryItems.objects.get(code='BT-001')
        self.save_manufacture(quantity=Decimal(25.0000))
        self.deliver_product(item=item, quantity=Decimal(20.0000))
        self.return_product(item=item, quantity=Decimal(5.0000))
        self.assertEqual(item.availability(), Decimal(10.0000))
