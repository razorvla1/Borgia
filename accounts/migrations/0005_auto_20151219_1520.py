# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-19 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20151219_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='balance',
            field=models.FloatField(default=0),
        ),
    ]
