# -*- coding: utf-8 -*-
# Generated by Django 1.11a1 on 2017-03-10 18:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0022_auto_20170310_1808'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('createdAt', models.DateField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'UserTracking',
                'verbose_name_plural': 'UserTrackings',
            },
        ),
    ]
