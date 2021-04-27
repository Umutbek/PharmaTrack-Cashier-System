import logging
from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from item.models import (GlobalItem, StoreOrderHistory,
                         Category, StoreItem, Store, Depot,
                         StoreOrder, ClientOrderedItem, ClientOrder,
                         CashierWorkShift, Report, StoreOrderItem)

logger = logging.getLogger(__name__)


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ('id', 'name', 'address', 'created_at', 'phone', 'email')


class DepotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Depot
        fields = ('id', 'name', 'address', 'created_at', 'phone', 'email')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')


class GlobalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalItem
        fields = ('id', 'unique_id', 'name', 'producer', 'category', 'image',
                  'description', 'series', 'max_num_pieces', 'expiration_date', 'price_selling')


class StoreItemSerializer(serializers.ModelSerializer):
    global_item = GlobalItemSerializer()

    class Meta:
        model = StoreItem
        fields = ('id', 'global_item', 'quantity', 'num_pieces', 'is_sale', 'store')
        read_only_fields = ('global_item', 'store')


class StoreOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreOrderItem
        fields = ('id', 'store_order', 'global_item', 'quantity', 'num_pieces', 'cost_one', 'cost_total')
        read_only_fields = ('store_order',)


class StoreOrderItemSerializerExtended(StoreItemSerializer):
    global_item = GlobalItemSerializer()


class StoreOrderSerializer(serializers.ModelSerializer):
    store_ordered_items = StoreOrderItemSerializer(many=True)

    class Meta:
        model = StoreOrder
        fields = ('id', 'store_ordered_items',
                  'depot', 'store', 'address',
                  'created_at', 'delivered_at', 'status',
                  'ordered_items_sum', 'ordered_items_cnt')
        read_only_fields = ('unique_id', 'delivered_at')
        extra_kwargs = {'depot': {'required': True},
                        'store': {'required': True}}

    @transaction.atomic
    def update(self, instance, validated_data):
        store_ordered_items = validated_data.get('store_ordered_items')
        instance.depot = validated_data.get('depot', instance.depot)
        instance.store = validated_data.get('store', instance.store)
        instance.address = validated_data.get('address', instance.address)
        instance.status = validated_data.get('status', instance.status)

        # проверяем, есть ли товары.
        # например, если вызывается метод PATCH
        if store_ordered_items:
            # удаляем все старые товары
            instance.store_ordered_items.all().delete()
            # добавляем обновленные товары
            for item in store_ordered_items:
                StoreOrderItem.objects.create(store_order=instance, **item)

        instance.save()
        return instance

    @transaction.atomic
    def create(self, validated_data):
        store_ordered_items = validated_data.pop('store_ordered_items')
        instance = StoreOrder.objects.create(**validated_data)
        for item in store_ordered_items:
            StoreOrderItem.objects.create(store_order=instance, **item)
        return instance


class StoreOrderSerializerExtended(StoreOrderSerializer):
    store_ordered_items = StoreOrderItemSerializerExtended(many=True)


class StoreOrderHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreOrderHistory
        fields = ('store_order_data', 'created_at')


class ClientOrderedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientOrderedItem
        fields = ('id', 'global_item', 'quantity',
                  'num_pieces', 'cost_one', 'cost_total')
        read_only_fields = ('id', 'cost_one', 'cost_total')


class ClientOrderSerializer(serializers.ModelSerializer):
    client_ordered_items = ClientOrderedItemSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ClientOrder
        fields = ('id', 'client_ordered_items', 'date_ordered', 'client', 'discount_price',
                  'cashier', 'store', 'ordered_items_cnt', 'ordered_items_sum')
        read_only_fields = ('unique_id', 'store')

    def validate(self, data):
        validated_data = super(ClientOrderSerializer, self).validate(data)
        client_ordered_items = validated_data.get("client_ordered_items")
        # store = validated_data.get('cashier').store
        store = 1
        errors = []
        for item_data in client_ordered_items:
            global_item = item_data.get('global_item')
            store_item = StoreItem.objects.get(store=store, global_item=global_item)

            qt = int(item_data.get('quantity'))
            num_pieces = int(item_data.get('num_pieces'))
            client_item_total_num_pieces = qt * global_item.max_num_pieces + num_pieces

            if store_item.total_num_pieces < client_item_total_num_pieces:
                errors.append({
                    'global_item': global_item.id,
                    'quantity': 'В аптеке недостаточное количество товаров!'
                })
        if errors:
            raise serializers.ValidationError({'client_ordered_items': errors})
        return data

    @transaction.atomic
    def create(self, validated_data):
        client_ordered_items = validated_data.pop("client_ordered_items", None)
        instance = ClientOrder.objects.create(**validated_data,
                                              store=validated_data.get('cashier').store,
                                              date_ordered=datetime.now())
        for item_params in client_ordered_items:
            ClientOrderedItem.objects.create(client_order=instance, **item_params)
        instance.save()
        instance.save_changes_in_store()
        return instance


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id', 'date_from', 'date_to', 'in_total',
                  'incomeTotal', 'earnTotal')
        read_only_fields = ('id', 'in_total', 'income_total', 'earn_total')


class CashierWorkShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = CashierWorkShift
        fields = '__all__'
