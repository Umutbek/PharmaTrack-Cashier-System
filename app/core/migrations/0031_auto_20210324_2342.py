# Generated by Django 3.1 on 2021-03-24 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20210324_2341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='type',
            field=models.CharField(choices=[(1, 'depot'), (2, 'store')], max_length=200, null=True),
        ),
    ]