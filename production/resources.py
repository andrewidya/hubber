from import_export.resources import ModelResource
from import_export.fields import Field

from production.models.manufacture import Manufacture, ProductUsage
from production.models.inventory import StockMovement


class ManufactureExportResource(ModelResource):
    datetime = Field(attribute='datetime', column_name='Datetime')
    customer__name = Field(attribute='customer__name', column_name='Customer')
    price = Field(attribute='price', column_name='Price')
    bill_of_material__code = Field(attribute='bill_of_material__code', column_name='BoM Code')
    bill_of_material__product__name = Field(attribute='bill_of_material__product__name',
                                            column_name='Product')
    quantity = Field(attribute='quantity', column_name='Quantity')
    unit__name = Field(attribute='unit__name', column_name='Unit')

    class Meta:
        model = Manufacture
        fields = ('datetime', 'customer__name', 'price', 'bill_of_material__code',
                  'bill_of_material__product__name','quantity', 'unit__name')


class ProductUsageExportResource(ModelResource):
    date = Field(attribute='manufacture__datetime__date', column_name='Date')
    item_code = Field(attribute='item__code', column_name='Item code')
    item_name = Field(attribute='item__name', column_name='Item name')
    product_name = Field(attribute='manufacture__bill_of_material__product__name',
                         column_name='Product name')
    quantity = Field(attribute='quantity', column_name='Quantity')
    unit = Field(attribute='unit__name', column_name='Unit')

    class Meta:
        model = ProductUsage
        fields = ('',)


class StockMovementExportResource(ModelResource):
    date = Field(attribute='datetime__date', column_name='Date')
    delivery_order = Field(attribute='delivery_order', column_name='Delivery Order')
    jo_number = Field(attribute='jo_number', column_name='JO Number')
    customer_name = Field(attribute='customer__name', column_name='Customer')
    item_name = Field(attribute='item__name', column_name='Item')
    status = Field(attribute='status', column_name='Status')
    quantity = Field(attribute='quantity', column_name='Quantity')
    unit = Field(attribute='unit__name', column_name='Unit')
    description = Field(attribute='description', column_name='Description')

    class Meta:
        model = StockMovement
        fields = ('',)
