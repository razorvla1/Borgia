# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 09:44
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lydia',
            name='time_operation',
        ),
        migrations.AddField(
            model_name='lydia',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2016, 3, 21, 10, 44, 19, 69057)),
        ),
    ]