# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-12-18 22:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_quovouser_didlink'),
        ('data', '0013_auto_20161124_1429'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quovoID', models.IntegerField()),
                ('date', models.DateField(blank=True, null=True)),
                ('fees', models.FloatField()),
                ('value', models.FloatField()),
                ('price', models.FloatField()),
                ('quantity', models.FloatField()),
                ('cusip', models.CharField(blank=True, max_length=10, null=True)),
                ('expense_category', models.CharField(blank=True, max_length=30, null=True)),
                ('ticker', models.CharField(blank=True, max_length=10, null=True)),
                ('ticker_name', models.CharField(blank=True, max_length=50, null=True)),
                ('tran_category', models.CharField(blank=True, max_length=50, null=True)),
                ('tran_type', models.CharField(blank=True, max_length=50, null=True)),
                ('quovoUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='userTransaction', to='dashboard.QuovoUser')),
            ],
            options={
                'verbose_name': 'Transaction',
                'verbose_name_plural': 'Transactions',
            },
        ),
    ]