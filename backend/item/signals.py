from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from item.models import GlobalItem, Store, StoreItem


@receiver(post_save, sender=GlobalItem)
def create_item_in_all_stores(sender, instance, **kwargs):
    for store in Store.objects.all():
        StoreItem.objects.create(global_item=instance, store=store)


@receiver(post_delete, sender=GlobalItem)
def delete_item_in_all_stores(sender, instance, **kwargs):
    for store in Store.objects.all():
        StoreItem.objects.filter(global_item=instance, store=store).delete()


@receiver(post_save, sender=Store)
def create_store_items_when_store_created(sender, instance, **kwargs):
    for item in GlobalItem.objects.all():
        StoreItem.objects.create(global_item=item, store=instance)
        

@receiver(post_delete, sender=Store)
def delete_store_items_when_store_deleted(sender, instance, **kwargs):
    for item in StoreItem.objects.filter(store=instance):
        item.delete()
