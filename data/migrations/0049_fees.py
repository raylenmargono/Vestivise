from __future__ import unicode_literals

import django
from django.db import migrations

from django.db import migrations, models



class Migration(migrations.Migration):

    dependencies = [
        ('data', '0048_merge_20170301_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.FloatField(default=0)),
                ('changeIndex', models.IntegerField(default=1)),
                ('quovoUser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees',
                                                to='dashboard.QuovoUser')),
            ],
            options={
                'verbose_name': 'UserFee',
                'verbose_name_plural': 'UserFees',
            },
        )
    ]