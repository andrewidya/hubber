# Generated by Django 2.1.5 on 2019-02-24 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0018_stockmovement_jo_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='manufacture',
            name='bom_output_standard',
            field=models.DecimalField(decimal_places=4, default=0, help_text='Jumlah output yang dikeluarkan oleh formula produksi, sesuai satuan dalam stock', max_digits=14, verbose_name='Standard output formula'),
        ),
    ]