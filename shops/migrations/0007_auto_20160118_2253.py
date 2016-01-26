# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-18 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shops', '0006_auto_20160118_2248'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productunit',
            name='description',
        ),
        migrations.RemoveField(
            model_name='productunit',
            name='name',
        ),
        migrations.RemoveField(
            model_name='shop',
            name='description',
        ),
        migrations.RemoveField(
            model_name='shop',
            name='name',
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=255),
        ),
    ]