# Generated by Django 2.1.5 on 2019-02-25 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0019_manufacture_bom_output_standard'),
    ]

    operations = [
        migrations.AddField(
            model_name='billofmaterial',
            name='output_standard',
            field=models.DecimalField(decimal_places=4, default=0, help_text='Jumlah output yang dikeluarkan oleh formula produksi, sesuai satuan dalam stock', max_digits=14, verbose_name='Standard output formula'),
        ),
    ]
