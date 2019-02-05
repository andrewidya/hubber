from decimal import  Decimal, getcontext

from django.contrib import admin
from django.conf.urls import url
from django.http.response import HttpResponse
from django.template import loader
from django.db.models import F, Sum, Value, OuterRef, Subquery

from import_export.admin import ImportExportMixin, ExportMixin

from production.models.customer import Customer, CustomerCategory, Supplier
from production.models.inventory import UnitMeasurement, InventoryItems, StockLevel, StockMovement
from production.models.manufacture import BillOfMaterial, BillOfMaterialDetails, Manufacture, ProductUsage
from production.resources import ManufactureExportResource

# Register your models here.
@admin.register(Customer)
class CustomerAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Customer Information', {
            'fields': ('name',),
        }),
    )
    search_fields = ('name',)
    list_display = ('name',)
    list_per_page = 25


@admin.register(CustomerCategory)
class CustomerCategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Customer Category Information', {
            'fields': ('name',),
        }),
    )
    search_fields = ('name',)


@admin.register(Supplier)
class SupplierAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Supplier Information', {
            'fields': ('name',),
        }),
    )
    search_fields = ('name',)
    list_per_page = 25


@admin.register(UnitMeasurement)
class UnitMeasurementAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(InventoryItems)
class InventoryItemAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Inventory Information', {
            'fields': (('code', 'type'), ('name', 'unit')),
        }),
    )
    raw_id_fields = ('unit',)
    autocomplete_lookup_fields = {
        'fk': ['unit'],
    }
    search_fields = ('code', 'name')
    list_filter = ('type', 'unit')
    list_display = ('code', 'name', 'type', 'total', 'unit')
    list_per_page = 25

    def total(self, obj):
        stock = obj.stock or Decimal(0.0000)
        usage = obj.usage or Decimal(0.0000)
        produce = Decimal(0.0000)
        if obj.produce:
            produce = Decimal(obj.produce)
        getcontext().prec = 9
        total = stock - usage + produce
        return total


@admin.register(StockLevel)
class StockLevelAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Stock Movement Details', {
            'fields': (('item', 'supplier'),('delivery_note', 'datetime'))
        }),
        ('Receipt Details', {
            'fields': (('quantity', 'price'), ('status', 'unit'))
        })
    )
    raw_id_fields = ('item', 'supplier', 'unit')
    autocomplete_lookup_fields = {
        'fk': ['item', 'supplier', 'unit'],
    }
    search_fields = ('item__name', 'supplier__name', 'delivery_note')
    list_filter = ('item__type', 'status', 'datetime')
    list_display = ('item', 'item_type', 'delivery_note', 'datetime',
                    'supplier', 'quantity', 'unit', 'status')
    list_per_page = 25
    change_list_template = 'admin/stocklevel/stocklevel_report_page.html'

    def save_model(self, request, obj, form, change):
        if obj.status == 'return':
            obj.quantity = obj.quantity * -1
        super().save_model(request, obj, form, change)


@admin.register(StockMovement)
class StockMovementAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Stock Movement Details', {
            'fields': ('customer', ('delivery_order', 'datetime'), 'status')
        }),
        ('Item Details', {
            'fields': ('item', ('quantity', 'unit'))
        }),
        ('Other Description', {
            'fields': ('description',)
        })
    )
    raw_id_fields = ('customer', 'item', 'unit')
    autocomplete_lookup_fields = {
        'fk': ['customer', 'item', 'unit'],
    }
    search_fields = ('item__name', 'customer__name', 'delivery_order')
    list_filter = ('status', 'datetime')
    list_display = ('item', 'customer', 'quantity', 'unit', 'datetime', 'status')
    list_per_page = 25


class BillOfMaterialDetailsInline(admin.TabularInline):
    model = BillOfMaterialDetails
    extra = 0
    raw_id_fields = ('material', 'unit')
    autocomplete_lookup_fields = {
        'fk': ['unit', 'material']
    }


def copy_bill_of_material(modeladmin, request, queryset):
    for query in queryset:
        details = query.billofmaterialdetails_set.all()
        query.pk = None
        query.save()
        for detail in details:
            detail.pk = None
            detail.bill_of_material = query
            detail.save()
copy_bill_of_material.short_description = "Copy Formula"


@admin.register(BillOfMaterial)
class BillOfMaterialAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Customer Order Information', {
            'fields': (('customer', 'customer_category'),),
        }),
        ('Product Details', {
            'fields': (('code', 'color_name'), ('product', 'price')),
        }),
        ('', {
            'fields': ('description',),
        })
    )
    raw_id_fields = ('customer', 'customer_category', 'product')
    autocomplete_lookup_fields = {
        'fk': ['customer', 'customer_category', 'product']
    }
    inlines = [BillOfMaterialDetailsInline]
    list_display = ('code', 'product', 'customer', 'customer_category', 'color_name')
    list_filter = ('color_name', 'customer', 'customer_category')
    search_fields = ('code', 'product__name', 'customer__name', 'color_name')
    list_per_page = 25
    actions = [copy_bill_of_material]


class ProductUsageInline(admin.TabularInline):
    model = ProductUsage
    extra = 0
    raw_id_fields = ['item', 'unit']
    autocomplete_lookup_fields = {
        'fk': ['item', 'unit']
    }


@admin.register(Manufacture)
class ManufactureAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Production Details', {
            'fields': (('datetime', 'customer'), ('price', 'bill_of_material'), ('quantity', 'unit')),
        }),
    )
    list_display = ('datetime', 'bill_of_material', '_product_name', 'price',
                    'customer', 'quantity', 'unit')
    search_fields = ('bill_of_material__code', 'bill_of_material__product__name')
    list_filter = ('datetime',)
    inlines = [ProductUsageInline]
    raw_id_fields = ['bill_of_material', 'customer', 'unit']
    list_per_page = 25
    autocomplete_lookup_fields = {
        'fk': ['bill_of_material', 'customer', 'unit']
    }
    resource_class = ManufactureExportResource

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.save()
            t_quantity = obj.quantity
            bom_details = BillOfMaterialDetails.objects.filter(bill_of_material=obj.bill_of_material)
            material_usage = []

            for i in bom_details:
                p = ProductUsage(item=i.material, manufacture=obj,
                                 quantity=(i.quantity * t_quantity), unit=i.unit)
                material_usage.append(p)

            ProductUsage.objects.bulk_create(material_usage)
        else:
            obj.save()


@admin.register(ProductUsage)
class ProductUsageAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('get_datetime', 'item', 'manufacture', 'quantity', 'unit')
    list_display_links = ('item',)
    search_fields = ('item__code', 'item__name')
    list_filter = ('manufacture__datetime', 'manufacture__bill_of_material')
    change_list_template = 'admin/productusage/productusage_report_page.html'

    def get_datetime(self, obj):
        return obj.manufacture.datetime
    get_datetime.short_description = "Datetime"

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        productusage_urls = [
            url(r'^print/$',
                self.admin_site.admin_view(self.print),
                name='{}_{}_print'.format(info[0], info[1]))
        ]

        return productusage_urls + urls

    def get_print_queryset(self, request):
        """
        Return print queryset.

        Default implementation respects applied search and filters.
        """
        list_display = self.get_list_display(request)
        list_display_links = self.get_list_display_links(request, list_display)
        list_filter = self.get_list_filter(request)
        search_fields = self.get_search_fields(request)
        if self.get_actions(request):
            list_display = ['action_checkbox'] + list(list_display)

        ChageList = self.get_changelist(request)
        changelist_kwargs = {
            'request': request,
            'model': self.model,
            'list_display': list_display,
            'list_display_links': list_display_links,
            'list_filter': list_filter,
            'date_hierarchy': self.date_hierarchy,
            'search_fields': search_fields,
            'list_select_related': self.list_select_related,
            'list_per_page': self.list_per_page,
            'list_max_show_all': self.list_max_show_all,
            'list_editable': self.list_editable,
            'model_admin': self,
            'sortable_by': self.sortable_by
        }
        cl = ChageList(**changelist_kwargs)
        return cl.get_queryset(request)


    def print(self, request):
        template = loader.get_template('admin/productusage/productusage_report_layout.html')
        queryset = self.get_print_queryset(request)

        units = UnitMeasurement.objects.filter(pk=OuterRef('unit__pk'))
        material_usages = queryset.values(
            datetime=F('manufacture__datetime'),
            item_pk=F('item__pk'),
            item_name=F('item__name'),
            product_name=F('manufacture__bill_of_material__product__name')
        ).annotate(
            usage=Sum('quantity'),
            units=Subquery(units.values('name')[:1])
        ).order_by('datetime')

        data_usage = []

        # sorting date range in selected/filtered queryset
        date_range = []
        for i in material_usages:
            if i['datetime'].date() not in date_range:
                date_range.append(i['datetime'].date())
        date_range.sort()

        # sorting actual data from queryset to be printed
        for current_date in date_range:
            container = {'date': current_date, 'data': [], 'total_data': 0}
            for recordset in material_usages:
                if recordset['datetime'].date() == current_date:
                    new_record = {}
                    new_record['item_pk'] = recordset['item_pk']
                    new_record['item_name'] = recordset['item_name']
                    new_record['product_name'] = recordset['product_name']
                    new_record['usage'] = recordset['usage']
                    new_record['unit'] = recordset['units']
                    container['data'].append(new_record)
                    container['total_data'] += 1
            data_usage.append(container)


        context = {
            'manufacture_list': data_usage,
        }

        print("breakpoint")
        return HttpResponse(template.render(context, request))
