# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-23 10:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0010_auto_20160223_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lydia',
            name='time_operation',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 23, 11, 15, 42, 228717)),
        ),
    ]
