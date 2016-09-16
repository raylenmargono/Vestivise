# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-28 06:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0026_auto_20160822_0534'),
    ]

    operations = [
        migrations.CreateModel(
            name='HoldingMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=80, null=True)),
                ('holdingType', models.CharField(blank=True, max_length=20, null=True)),
                ('cusipNumber', models.CharField(blank=True, max_length=9, null=True)),
                ('symbol', models.CharField(blank=True, max_length=20, null=True)),
                ('ric', models.CharField(blank=True, max_length=9, null=True)),
                ('completed', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'HoldingMetaData',
                'verbose_name_plural': 'HoldingMetaDatas',
            },
        ),
        migrations.RemoveField(
            model_name='holding',
            name='cusipNumber',
        ),
        migrations.RemoveField(
            model_name='holding',
            name='description',
        ),
        migrations.RemoveField(
            model_name='holding',
            name='holdingType',
        ),
        migrations.RemoveField(
            model_name='holding',
            name='symbol',
        ),
    ]