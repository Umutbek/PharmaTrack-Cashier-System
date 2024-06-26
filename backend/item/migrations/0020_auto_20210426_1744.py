# Generated by Django 3.1 on 2021-04-26 11:44

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0019_auto_20210426_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='storeorder',
            name='status',
            field=django_fsm.FSMIntegerField(choices=[(1, 'Новый'), (2, 'Отгружено'), (3, 'Доставлено')], default=1),
        ),
        migrations.AlterField(
            model_name='clientorder',
            name='status',
            field=models.IntegerField(choices=[(1, 'Новый'), (2, 'Отгружено'), (3, 'Доставлено')], default=1),
        ),
    ]
