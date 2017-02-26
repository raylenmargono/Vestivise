# -*- coding: utf-8 -*-
# Generated by Django 1.11a1 on 2017-02-25 21:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0017_progresstracker'),
    ]

    operations = [
        migrations.AddField(
            model_name='progresstracker',
            name='annotation_view_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='progresstracker',
            name='did_hover_module',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='progresstracker',
            name='did_open_dashboard',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='progresstracker',
            name='total_dashboard_view_time',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='progresstracker',
            name='total_filters',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='progresstracker',
            name='tutorial_time',
            field=models.IntegerField(default=0),
        ),
    ]
