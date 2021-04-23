# Generated by Django 3.1 on 2021-04-23 06:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_auto_20210421_1252'),
        ('item', '0010_storeorder_next'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clientorder',
            name='count_item',
        ),
        migrations.RemoveField(
            model_name='clientorder',
            name='total_sum',
        ),
        migrations.RemoveField(
            model_name='clientordereditem',
            name='cost_one',
        ),
        migrations.RemoveField(
            model_name='clientordereditem',
            name='cost_total',
        ),
        migrations.RemoveField(
            model_name='storeitem',
            name='price_received',
        ),
        migrations.RemoveField(
            model_name='storeitem',
            name='price_sale',
        ),
        migrations.AddField(
            model_name='clientorder',
            name='store',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='client_orders', to='item.store'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clientorder',
            name='cashier',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='client_orders', to='user.cashier'),
            preserve_default=False,
        ),
    ]