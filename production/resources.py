from import_export.resources import ModelResource
from import_export.fields import Field
from production.models.manufacture import Manufacture


class ManufactureExportResource(ModelResource):
    datetime = Field(attribute='datetime', column_name='Datetime')
    customer__name = Field(attribute='customer__name', column_name='Customer')
    price = Field(attribute='price', column_name='Price')
    bill_of_material__code = Field(attribute='bill_of_material__code', column_name='BoM Code')
    bill_of_material__product__name = Field(attribute='bill_of_material__product__name', column_name='Product')
    quantity = Field(attribute='quantity', column_name='Quantity')
    unit__name = Field(attribute='unit__name', column_name='Unit')

    class Meta:
        model = Manufacture
        fields = ('datetime', 'customer__name', 'price', 'bill_of_material__code',
                  'bill_of_material__product__name','quantity', 'unit__name')