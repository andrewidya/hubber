# Generated by Django 2.1.5 on 2019-02-13 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0012_auto_20190213_0827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitems',
            name='available',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=14, verbose_name='Available'),
        ),
    ]