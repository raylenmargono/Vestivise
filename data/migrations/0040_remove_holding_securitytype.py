# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-02-12 18:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0039_auto_20170212_1739'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='holding',
            name='securityType',
        ),
    ]