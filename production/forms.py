from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import AdminDateWidget

from production.models.manufacture import ProductUsage


PRODUCT_USAGE_REPORT = [
    ('material', 'Penggunaan Material'),
    ('product', 'Output Produksi')
]

class ProductUsageReportForm(forms.Form):
    start_date = forms.DateField(widget=AdminDateWidget)
    end_date = forms.DateField(widget=AdminDateWidget)
    report_type = forms.ChoiceField(choices=PRODUCT_USAGE_REPORT)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    _("Tanggal akhir tidak boleh kurang / sebelum "
                      "tanggal awal")
                )


class ProductUsageInlineForm(forms.ModelForm):
    class Meta:
        model = ProductUsage
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        qty = cleaned_data['quantity']
        item = cleaned_data['item']

        if qty > item.available:
            raise forms.ValidationError(
                _("Jumlah stock yang tersedia tidak mencukupi")
            )
        else:
            return cleaned_data
