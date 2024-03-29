import numpy as np
import pandas as pd

from django.contrib import admin
from django.urls import path
from django.template.response import TemplateResponse

from django.db.models import F, Q
from django.contrib import messages
from django.utils import timezone

from import_export.admin import ImportExportMixin, ExportMixin
from rangefilter.filter import DateRangeFilter

from production.models.customer import Customer, CustomerCategory, Supplier
from production.models.inventory import UnitMeasurement, InventoryItems, StockLevel, \
    StockMovement, InventoryAdjustment
from production.models.manufacture import BillOfMaterial, BillOfMaterialDetails, \
    Manufacture, ProductUsage
from production.resources import ManufactureExportResource, ProductUsageExportResource, \
    StockMovementExportResource
from production.forms import ProductUsageReportForm, ProductUsageInlineForm, StockMovementForm
from html2pdf.response import HTML2PDFResponse

# Register your models here.
class BasePrintAdmin(object):
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

        Changelist = self.get_changelist(request)
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
        cl = Changelist(**changelist_kwargs)
        return cl.get_queryset(request)


@admin.register(Customer)
class CustomerAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Customer Information', {
            'fields': ('name',),
        }),
    )
    search_fields = ('name',)
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name')
    list_per_page = 25


@admin.register(CustomerCategory)
class CustomerCategoryAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Customer Category Information', {
            'fields': ('name',),
        }),
    )
    search_fields = ('name',)
    list_display = ('id', 'name')
    list_display_links = ('id', 'name')


@admin.register(Supplier)
class SupplierAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Supplier Information', {
            'fields': ('name',),
        }),
    )
    search_fields = ('name',)
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)
    list_per_page = 25


@admin.register(UnitMeasurement)
class UnitMeasurementAdmin(ImportExportMixin, admin.ModelAdmin):
    search_fields = ('name',)
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)


@admin.register(InventoryItems)
class InventoryItemAdmin(ImportExportMixin, BasePrintAdmin, admin.ModelAdmin):
    fieldsets = (
        ('Inventory Information', {
            'fields': (('code', 'type'), ('name', 'unit'), ('price', 'initial')),
        }),
    )
    raw_id_fields = ('unit',)
    autocomplete_lookup_fields = {
        'fk': ['unit'],
    }
    search_fields = ('code', 'name')
    list_filter = ('type', 'unit')
    list_display_links = ('id', 'code',)
    list_display = ('id', 'code', 'name', 'type', 'initial', 'availability' ,'unit', 'price')
    list_per_page = 15
    change_list_template = 'admin/inventory/inventory_item_report_page.html'

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        inventory_urls = [
            path('print/',
                    self.admin_site.admin_view(self.print_itenvetoryitem),
                    name='{}_{}_print'.format(info[0], info[1]))
        ]

        return inventory_urls + urls

    def print_itenvetoryitem(self, request):
        object = self.get_print_queryset(request)
        template = 'admin/inventory/inventory_item_pdf_layout.html'
        date = timezone.now()
        context = {
            'item_list': object,
            'page_title': "Daftar Persediaan Inventory",
            'date': date
        }
        return HTML2PDFResponse(
            request, template, context,
            filename="Inventory Stock Card - {}.pdf".format(date.date())
        )


@admin.register(InventoryAdjustment)
class InventoryAdjustmentAdmin(admin.ModelAdmin):
    fields = (('item', 'quantity'), )
    list_display = ('item', 'quantity', 'last_edited', 'first_created')
    raw_id_fields = ['item',]
    autocomplete_lookup_fields = {
        'fk': ['item',]
    }


@admin.register(StockLevel)
class StockLevelAdmin(ImportExportMixin, BasePrintAdmin, admin.ModelAdmin):
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
    list_filter = ('item__type', 'status', 'datetime', ('datetime', DateRangeFilter))
    list_display = ('item', 'item_type', 'delivery_note', 'datetime',
                    'supplier', 'quantity', 'unit', 'status')
    list_per_page = 25
    change_list_template = 'admin/stocklevel/stocklevel_report_page.html'

    def save_model(self, request, obj, form, change):
        if obj.status == 'return':
            obj.quantity *= -1
        super().save_model(request, obj, form, change)

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        purchasing_urls = [
            path('print/',
                    self.admin_site.admin_view(self.print_purchasing),
                    name='{}_{}_print'.format(info[0], info[1]))
        ]
        return purchasing_urls + urls

    def print_purchasing(self, request):
        queryset = self.get_print_queryset(request)
        page_title = "Daftar Pembelian Baranag"
        date = timezone.now()
        data = dict(date=[], product_code=[], product_name=[], status=[], quantity=[])
        for i in queryset:
            data['date'].append(i.datetime.date())
            data['product_code'].append(i.item.code)
            data['product_name'].append(i.item.name)
            data['status'].append(i.status)
            data['quantity'].append(i.quantity)

        data_frame = pd.DataFrame(data=data)
        data_frame['quantity'] = data_frame['quantity'].astype(float)
        pivot = pd.pivot_table(
            data_frame.round(3),
            index=['date', 'product_code', 'product_name', 'status'],
            values='quantity',
            fill_value=0
        )
        template = 'admin/stocklevel/stocklevel_print_pdf_layout.html'
        context = {
            'delivery_list': pivot.to_html(classes=['minimalistBlack']),
            'page_title': page_title,
            'date': date
        }

        return HTML2PDFResponse(
            request, template, context=context,
            filename="Purchasing - {}.pdf".format(date.date())
        )


@admin.register(StockMovement)
class StockMovementAdmin(ImportExportMixin, BasePrintAdmin, admin.ModelAdmin):
    fieldsets = (
        ('Stock Movement Details', {
            'fields': (('customer', 'jo_number'), ('delivery_order', 'datetime'), 'status')
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
    list_filter = ('status', 'datetime', ('datetime', DateRangeFilter))
    list_display = ('item', 'customer', 'jo_number', 'quantity', 'unit', 'datetime', 'status')
    list_per_page = 25
    form = StockMovementForm
    resource_class = StockMovementExportResource
    change_list_template = 'admin/stockmovement/stockmovement_report_page.html'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['status',]
        else:
            return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        delivery_urls = [
            path('print/',
                    self.admin_site.admin_view(self.print_delivery),
                    name='{}_{}_print'.format(info[0], info[1]))
        ]
        return delivery_urls + urls

    def print_delivery(self, request):
        queryset = self.get_print_queryset(request)
        page_title = "Daftar Pengiriman Barang"
        date = timezone.now()
        data = dict(date=[], product_code=[], product_name=[], jo_number=[], status=[], quantity=[])
        for i in queryset:
            data['date'].append(i.datetime.date())
            data['product_code'].append(i.item.code)
            data['product_name'].append(i.item.name)
            data['jo_number'].append(i.jo_number)
            data['status'].append(i.status)
            data['quantity'].append(i.quantity)

        data_frame = pd.DataFrame(data=data)
        data_frame['quantity'] = data_frame['quantity'].astype(float)
        pivot = pd.pivot_table(
            data_frame.round(3),
            index=['date', 'product_code', 'product_name', 'jo_number', 'status'],
            values='quantity',
            fill_value=0
        )
        template = 'admin/stockmovement/stockmovement_pdf_layout.html'
        context = {
            'delivery_list': pivot.to_html(classes=['minimalistBlack']),
            'page_title': page_title,
            'date': date
        }

        return HTML2PDFResponse(
            request, template, context=context,
            filename="Delivery - {}.pdf".format(date.date())
        )


class BillOfMaterialDetailsInline(admin.TabularInline):
    model = BillOfMaterialDetails
    extra = 0
    fields = ('material', 'quantity', 'unit')
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
            'fields': (('code', 'color_name'), ('product',)),
        }),
        ('', {
           'fields': ('output_standard',),
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
    readonly_fields = ['output_standard']
    list_display = ('code', 'product', 'customer', 'customer_category', 'color_name')
    list_filter = ('color_name', 'customer', 'customer_category')
    search_fields = ('code', 'product__name', 'customer__name', 'color_name')
    list_per_page = 25
    actions = [copy_bill_of_material]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.output_standard = obj.output_weight()
        obj.save()


@admin.register(BillOfMaterialDetails)
class BillOfMaterialDetailsAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('bill_of_material', 'material', 'quantity', 'unit')


class ProductUsageInline(admin.TabularInline):
    model = ProductUsage
    extra = 0
    raw_id_fields = ['item', 'unit']
    autocomplete_lookup_fields = {
        'fk': ['item', 'unit']
    }
    form = ProductUsageInlineForm


@admin.register(Manufacture)
class ManufactureAdmin(ImportExportMixin, admin.ModelAdmin):
    fieldsets = (
        ('Production Details', {
            'fields': (('customer', 'datetime'), ('bill_of_material', 'price'), ('unit', 'quantity')),
        }),
    )
    list_display = ('datetime', 'bill_of_material', '_product_name', 'price',
                    'customer', 'quantity', 'unit', 'status')
    search_fields = ('bill_of_material__code', 'bill_of_material__product__name')
    readonly_fields = ('price', 'bom_output_standard')
    list_editable = ('status',)
    list_filter = ('datetime',('datetime', DateRangeFilter))
    inlines = [ProductUsageInline]
    raw_id_fields = ['bill_of_material', 'customer', 'unit']
    list_per_page = 25
    autocomplete_lookup_fields = {
        'fk': ['bill_of_material', 'customer', 'unit']
    }
    resource_class = ManufactureExportResource
    change_form_template = 'admin/manufacture/change_form.html'

    def save_model(self, request, obj, form, change):
        if obj.id == None:
            obj.save()
            t_qty = obj.quantity
            bom = BillOfMaterialDetails.objects.filter(bill_of_material=obj.bill_of_material)
            bom_output_weight = obj.bill_of_material.output_weight()
            mtr_used = []

            msgs = []
            for i in bom:
                p = ProductUsage(
                    item=i.material, manufacture=obj,
                    quantity=((i.quantity / bom_output_weight) * t_qty), unit=i.unit
                )
                if p.quantity > p.item.availability():
                    msgs.append("Stock \"{} - {}\" tidak mencukupi".format(p.item.code, p.item.name))
                else:
                    p.price = p.quantity * i.material.price
                    mtr_used.append(p)

            if msgs:
                for i in msgs:
                    messages.add_message(request, messages.ERROR, i)
                info_msg = "Hapus record produksi \"{} - {} untuk {} tanggal {}\" agar " \
                           "tidak mempengaruhi nilai stock".format(obj.bill_of_material.product.code,
                                                                   obj.bill_of_material.product.name,
                                                                   obj.customer.name,
                                                                   obj.datetime)
                messages.add_message(request, messages.INFO, info_msg)

            ProductUsage.objects.bulk_create(mtr_used)

        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        obj = form.instance
        obj.save()

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        manufacture_urls = [
            path('<int:object_id>/print/',
                    self.admin_site.admin_view(self.print_bill_of_material),
                    name='{}_{}_print'.format(info[0], info[1]))
        ]

        return manufacture_urls + urls

    def print_bill_of_material(self, request, object_id):
        manufacture = Manufacture.objects.get(pk=object_id)
        filters = (Q(item__type='TTD') | Q(item__type='BT'))
        product_usage = ProductUsage.objects.filter(manufacture=manufacture).exclude(item__type='CON')
        consumable = ProductUsage.objects.filter(manufacture=manufacture).exclude(filters)
        context = {
            'manufacture': manufacture,
            'product_usage': product_usage,
            'consumable': consumable,
        }

        return HTML2PDFResponse(
            request, 'admin/manufacture/manufacture_order_report.html',
            context=context, filename='BoM-{}.pdf'.format(manufacture.datetime.date())
        )


@admin.register(ProductUsage)
class ProductUsageAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('get_datetime', 'item', 'manufacture', 'quantity', 'unit')
    list_display_links = ('item',)
    search_fields = ('item__code', 'item__name')
    list_filter = ('manufacture__datetime', 'manufacture__bill_of_material',
                   ('manufacture__datetime', DateRangeFilter))
    change_list_template = 'admin/productusage/productusage_report_page.html'
    resource_class = ProductUsageExportResource

    def get_datetime(self, obj):
        return obj.manufacture.datetime
    get_datetime.short_description = "Datetime"

    def get_urls(self):
        urls = super().get_urls()
        info = self.get_model_info()
        productusage_urls = [
            path('print/',
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

    def _get_dataframe(self, queryset):
        data = dict(date=[], item_code=[], item_name=[], unit=[], product=[],
                    product_code=[], quantity=[])
        for i in queryset:
            data['date'].append(i['datetime'].date())
            data['item_code'].append(i['item_code'])
            data['item_name'].append(i['item_name'])
            data['unit'].append(i['item_unit_name'])
            data['product_code'].append(i['product_code'])
            data['product'].append(i['product_name'])
            data['quantity'].append(i['usage'])

        data_frame = pd.DataFrame(data=data)
        return data_frame

    def _pivoting_by_materialused(self, queryset):
        data_frame = self._get_dataframe(queryset)
        data_frame['quantity'] = data_frame['quantity'].astype(float)
        pivot = pd.pivot_table(
            data_frame.round(3),
            index=['date', 'item_code', 'item_name', 'unit', 'product_code', 'product'],
            values='quantity',
            aggfunc=np.sum,
            fill_value=0
        )
        return pivot.to_html(classes=['minimalistBlack'])

    def _pivoting_materialused_sum(self, queryset):
        data_frame = self._get_dataframe(queryset)
        data_frame['quantity'] = data_frame['quantity'].astype(float)
        pivot = pd.pivot_table(
            data_frame.round(3),
            index=['date', 'item_code', 'item_name'],
            values='quantity',
            aggfunc=np.sum,
            fill_value=0
        )
        return pivot.to_html(classes=['minimalistBlack'])

    def _pivoting_product_output(self, queryset):
        data_frame = self._get_dataframe(queryset)
        data_frame['quantity'] = data_frame['quantity'].astype(float)
        pivot = pd.pivot_table(
            data_frame.round(3),
            index=['date', 'product_code', 'product', 'item_code', 'item_name', 'unit'],
            values='quantity',
            aggfunc=np.sum,
            fill_value=0
        )
        return pivot.to_html(classes=['minimalistBlack'])

    def _pivoting_product_output_summary(self, queryset):
        data = dict(date=[], product_code=[], product_name=[], unit=[], quantity=[], price=[])

        for i in queryset:
            data['date'].append(i['date_time'].date())
            data['product_code'].append(i['product_code'])
            data['product_name'].append(i['product_name'])
            data['unit'].append(i['unit_name'])
            data['quantity'].append(i['qty'])
            data['price'].append(i['total'])

        data_frame = pd.DataFrame(data=data)
        data_frame['quantity'] = data_frame['quantity'].astype(float)
        data_frame['price'] = data_frame['price'].astype(float)
        pivot = pd.pivot_table(
            data_frame.round(3),
            index=['date', 'product_code', 'product_name', 'unit'],
            values='quantity',
            aggfunc=np.sum,
            fill_value=0
        )
        return pivot.to_html(classes=['minimalistBlack'])

    def print(self, request):
        form = ProductUsageReportForm(request.POST or None)

        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            report_type = form.cleaned_data['report_type']
            context = {}
            template = 'admin/productusage/productusage_report_layout.html'

            material = ProductUsage.objects.filter(
                manufacture__datetime__date__range=[start_date, end_date]
            ).select_related(
                'manufacture', 'item', 'manufacture__bill_of_material__product'
            ).values(
                datetime=F('manufacture__datetime'),
                item_pk=F('item__pk'),
                item_code=F('item__code'),
                item_name=F('item__name'),
                item_unit_name=F('item__unit__name'),
                product_code=F('manufacture__bill_of_material__product__code'),
                product_name=F('manufacture__bill_of_material__product__name'),
                usage=F('quantity'),
                unit_name=F('unit__name')
            ).order_by(
                'manufacture__datetime__date', 'item'
            )

            if report_type == 'material':
                data_mat = self._pivoting_by_materialused(material)
                data_sum = self._pivoting_materialused_sum(material)
                context['page_title'] = "Summary Penggunaan Material - Periode {} - {}".format(
                    start_date, end_date
                )
                context['report'] = data_mat
                context['summary'] = data_sum

            if report_type == 'product':
                manufacture = Manufacture.objects.filter(
                    datetime__date__range=[start_date, end_date]
                ).values(
                    date_time=F('datetime'),
                    bom=F('bill_of_material'),
                    product_code=F('bill_of_material__product__code'),
                    product_name=F('bill_of_material__product__name'),
                    unit_name=F('unit__name'),
                    qty=F('quantity'),
                    total=F('price'),
                ).order_by(
                    'datetime__date', 'bill_of_material__product__name'
                )

                data_mat = self._pivoting_product_output(material)
                data_sum = self._pivoting_product_output_summary(manufacture)
                context['page_title'] = "Summary Penggunaan Material per Output Produksi - Periode {} - {}".format(
                    start_date, end_date
                )
                context['report'] = data_mat
                context['summary'] = data_sum

            return HTML2PDFResponse(
                request, template, context,
                filename="{}-{}-{}.pdf".format(start_date, end_date, report_type)
            )

        opts = self.model._meta
        context = dict(self.admin_site.each_context(request), opts=opts, form=form)
        return TemplateResponse(request, 'admin/productusage/productusage_report.html', context=context)
