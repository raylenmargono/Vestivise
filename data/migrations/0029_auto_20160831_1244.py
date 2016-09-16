# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-31 12:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0028_holding_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='holding',
            name='metaData',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='holdingFromMetaData', to='data.HoldingMetaData'),
        ),
        migrations.AlterField(
            model_name='refreshinfo',
            name='statusMessage',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]