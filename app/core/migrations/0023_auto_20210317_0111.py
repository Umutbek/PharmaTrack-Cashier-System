# Generated by Django 3.1 on 2021-03-16 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20210317_0048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmstoreitems',
            name='cost',
            field=models.FloatField(null=True),
        ),
    ]
