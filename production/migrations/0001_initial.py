# Generated by Django 2.1.5 on 2019-01-30 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, verbose_name='Name')),
            ],
            options={
                'verbose_name': '1.1. Customer',
                'verbose_name_plural': '1.1. Customer List',
            },
        ),
        migrations.CreateModel(
            name='CustomerCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, verbose_name='Name')),
            ],
            options={
                'verbose_name': '1.2. Customer Category',
                'verbose_name_plural': '1.2. Customer Categories',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45, verbose_name='Name')),
            ],
            options={
                'verbose_name': '1.3 Supplier',
                'verbose_name_plural': '1.3 Supplier List',
            },
        ),
    ]
