# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-24 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0022_auto_20161224_0621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='averageusersharpe',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
