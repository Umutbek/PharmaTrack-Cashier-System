# Generated by Django 3.1 on 2021-04-27 04:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('item', '0022_storeorderhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='storeorder',
            old_name='date_sent',
            new_name='created_at',
        ),
        migrations.RenameField(
            model_name='storeorder',
            old_name='date_received',
            new_name='delivered_at',
        ),
        migrations.RemoveField(
            model_name='storeitem',
            name='parts',
        ),
        migrations.RemoveField(
            model_name='storeorder',
            name='is_editable',
        ),
    ]