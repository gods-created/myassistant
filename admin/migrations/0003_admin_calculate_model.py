# Generated by Django 4.2.16 on 2025-02-14 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0002_alter_admin_managers'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='calculate_model',
            field=models.CharField(default=None, max_length=250, null=True),
        ),
    ]
