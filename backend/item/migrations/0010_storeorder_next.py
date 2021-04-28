# Generated by Django 3.1 on 2021-04-22 09:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0009_auto_20210422_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeorder',
            name='next',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='prev', to='item.storeorder'),
        ),
    ]
