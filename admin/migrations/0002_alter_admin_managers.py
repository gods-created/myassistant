# Generated by Django 4.2.19 on 2025-02-13 13:35

import admin.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='admin',
            managers=[
                ('objects', admin.managers.AdminManager()),
            ],
        ),
    ]
