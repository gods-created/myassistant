# Generated by Django 4.2.16 on 2025-02-16 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0003_admin_calculate_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='lm_model',
            field=models.CharField(default=None, max_length=250, null=True),
        ),
    ]
