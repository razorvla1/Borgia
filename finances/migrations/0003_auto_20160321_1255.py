# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 11:55
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0002_auto_20160321_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lydia',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2016, 3, 21, 12, 55, 36, 616405)),
        ),
    ]
