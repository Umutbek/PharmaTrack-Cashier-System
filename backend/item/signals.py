# from django.db.models.signals import pre_save
# from django.dispatch import receiver
# from item.models import StoreOrderItem, StoreItem
# from rest_framework import serializers
#
#
# @receiver(pre_save, sender=StoreOrderItem)
# def change_store_item_quantity(sender, instance, *args, **kwargs):
#     global_item = instance.global_item
#     try:
#         store_item = StoreItem.objects.get(global_item=global_item)
#     except StoreItem.DoesNotExist:
#         raise serializers.ValidationError({'global_item': 'Такого товара нет в аптеке!'})
#
#     if instance:
#         raise serializers.ValidationError('Нельзя изменять уже заказанные товары')
#     if not store_item.quantity >= instance.quantity:
#         raise serializers.ValidationError({'quantity': 'В аптеке недостаточно количеств указанного товара!'})
#     else:
#         store_item.quantity -= instance.quantity
#         store_item.save()
