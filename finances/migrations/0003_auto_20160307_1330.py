# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-07 12:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0002_auto_20160303_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lydia',
            name='time_operation',
            field=models.DateTimeField(default=datetime.datetime(2016, 3, 7, 13, 30, 42, 966920)),
        ),
    ]
