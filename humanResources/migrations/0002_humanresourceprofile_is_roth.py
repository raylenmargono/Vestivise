# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-10-08 23:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('humanResources', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='humanresourceprofile',
            name='is_roth',
            field=models.BooleanField(default=False),
        ),
    ]
