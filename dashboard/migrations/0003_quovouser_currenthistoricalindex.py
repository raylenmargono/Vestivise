# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-09 18:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_auto_20161008_2159'),
    ]

    operations = [
        migrations.AddField(
            model_name='quovouser',
            name='currentHistoricalIndex',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
