from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from production.models.inventory import InventoryItems, UnitMeasurement,\
    InventoryAdjustment, StockMovement, StockLevel
from production.models.customer import Supplier, Customer, CustomerCategory
from production.models.manufacture import Manufacture, ProductUsage, \
    BillOfMaterial, BillOfMaterialDetails


class InventoryItemTest(TestCase):
    def setUp(self):
        unit = UnitMeasurement.objects.create(name='Kg')
        Supplier.objects.create(name="PT Maju Jasa Semarang")
        customer = Customer.objects.create(name="Mukidi Jaya")
        cust_cat = CustomerCategory.objects.create(name="Rokok")
        item = InventoryItems.objects.create(
            code='MTR001', name='Cat Merah', type='TTD',
            unit=unit, price=Decimal(1500.0000),
            initial=Decimal(20.0000), available=0
        )
        product = InventoryItems.objects.create(
            code='BJ001', name='Cat Merah Muda', type='BT',
            unit=unit, price=Decimal(2000.0000),
            initial=Decimal(0.0000), available=0
        )
        bom = BillOfMaterial.objects.create(
            code="FR001", customer=customer, customer_category=cust_cat,
            color_name="Cat Merah Muda", product=product,
            price=Decimal(20000.0000)
        )
        bom_details = BillOfMaterialDetails.objects.create(
            bill_of_material=bom, material=item, quantity=Decimal(4.0000),
            unit=unit, price=Decimal(1500.0000)
        )
        Manufacture.objects.create(
            datetime=timezone.now(), bill_of_material=bom, price=Decimal(20000.0000),
            customer=customer, quantity=Decimal(2.0000), unit=unit, status='done'
        )

    def test_purchased(self):
        item = InventoryItems.objects.get(code='MTR001')
        supplier = Supplier.objects.get(name="PT Maju Jasa Semarang")

        self.assertEqual(item.purchased(), Decimal(0.0000))

        StockLevel.objects.create(
            item=item, delivery_note="12345", datetime=timezone.now(),
            quantity=Decimal(10.0000), unit=item.unit, status='receipt',
            supplier=supplier, price=Decimal(1500.0000)
        )

        self.assertEqual(item.purchased(), Decimal(10.0000))
        self.assertEqual(item.availability(), Decimal(30.0000))


    def test_produced(self):
        item = InventoryItems.objects.get(code='MTR001')
        self.assertEqual(item.produced(), Decimal(0.0000))

    def test_used(self):
        item = InventoryItems.objects.get(code='MTR001')

        self.assertEqual(item.used(), Decimal(0.0000))

        manufacture = Manufacture.objects.get(pk=1)
        ProductUsage.objects.create(
            item=item, manufacture=manufacture, price=Decimal(1500.0000),
            quantity=2, unit=item.unit
        )

        self.assertEqual(item.used(), Decimal(2.0000))
        self.assertEqual(item.availability(), Decimal(18.0000))

    def test_delivered(self):
        item = InventoryItems.objects.get(code='MTR001')
        self.assertEqual(item.delivered(), Decimal(0.0000))

    def test_adjustment(self):
        item = InventoryItems.objects.get(code='MTR001')
        print(item.adjustment())
        self.assertEqual(item.adjustment(), Decimal(0.0000))

    def test_availability(self):
        item = InventoryItems.objects.get(code='MTR001')
        self.assertEqual(item.availability(), Decimal(20.0000))
