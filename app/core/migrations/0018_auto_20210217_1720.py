# Generated by Django 3.1 on 2021-02-17 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_itemsin_iseditable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='costin',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
