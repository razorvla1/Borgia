# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-25 17:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lydia',
            old_name='recipient_user_id',
            new_name='recipient',
        ),
        migrations.RenameField(
            model_name='lydia',
            old_name='sender_user_id',
            new_name='sender',
        ),
    ]