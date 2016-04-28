# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-28 14:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20160418_2129'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('last_call_datetime', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NotificationTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message_template', models.TextField()),
                ('target_template', models.CharField(max_length=20)),
                ('category_template', models.CharField(choices=[('ADMIN', 'admin'), ('FUNDS', 'funds'), ('FOYER', 'foyer'), ('AUBERGE', 'auberge'), ('OTHER', 'other')], default='OTHER', max_length=10)),
                ('type_template', models.CharField(choices=[('DEBUG', 'debug'), ('SUCCESS', 'success'), ('INFO', 'info'), ('WARNING', 'warning'), ('ERROR', 'error')], default='INFO', max_length=10)),
                ('creation_datetime', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('last_call_datetime', models.DateTimeField(blank=True, null=True)),
                ('is_activated', models.BooleanField(default=False)),
                ('notification_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notifications.NotificationClass')),
            ],
        ),
    ]