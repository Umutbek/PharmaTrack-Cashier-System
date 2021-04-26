from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from item.models import (GlobalItem,
                         Category, StoreItem, Store, Depot,
                         StoreOrder, ClientOrderedItem, ClientOrder,
                         CashierWorkShift, Report, StoreOrderItem)

from item.constants import StoreOrderStatuses


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
        fields = ('id', 'global_item', 'quantity', 'num_pieces', 'parts', 'is_sale', 'store')
        read_only_fields = ('global_item', 'store')


class StoreOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreOrderItem
        fields = ('id', 'store_order', 'global_item', 'quantity', 'num_pieces', 'cost_total')
        read_only_fields = ('store_order',)


class StoreOrderSerializer(serializers.ModelSerializer):
    store_ordered_items = StoreOrderItemSerializer(many=True)

    class Meta:
        model = StoreOrder
        fields = ('id', 'store_ordered_items',
                  'depot', 'store', 'address',
                  'date_sent', 'date_received', 'is_editable', 'status')
        read_only_fields = ('date_received', 'is_editable', 'unique_id', 'status')
        extra_kwargs = {'depot': {'required': True},
                        'store': {'required': True}}

    def update(self, instance, validated_data):
        if instance.status == StoreOrderStatuses.DELIVERED:
            raise serializers.ValidationError({'status': 'Этот заказ нельзя менять!'})
        # todo: save history of updates
        return instance

    @transaction.atomic
    def create(self, validated_data):
        store_ordered_items = validated_data.pop('store_ordered_items')
        store_order = StoreOrder.objects.create(**validated_data)
        for item in store_ordered_items:
            StoreOrderItem.objects.create(store_order=store_order, **item)
        return store_order
        # todo: date_received should be automatically set
        # todo: can't edit if is_editable false


class ClientOrderedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientOrderedItem
        fields = ('id', 'global_item', 'quantity', 'sepparts',
                  'date_ordered', 'cost_one', 'cost_total')
        read_only_fields = ('id', 'cost_one', 'cost_total')


class ClientOrderSerializer(serializers.ModelSerializer):
    client_ordered_items = ClientOrderedItemSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ClientOrder
        fields = ('id', 'client_ordered_items', 'date_ordered',
                  'cashier', 'store', 'items_cnt', 'items_sum')
        extra_kwargs = {
            'items_cnt': {'read_only': True},
            'items_sum': {'read_only': True},
            'unique_id': {'read_only': True},
            'store': {'read_only': True}
        }

    def validate(self, data):
        store = data.get('cashier').store
        errors = []
        for item in data.get('client_ordered_items'):
            global_item = item.get('global_item')
            try:
                store_item = StoreItem.objects.get(global_item=global_item, store=store)
            except StoreItem.DoesNotExist:
                errors.append({'global_item': 'В аптеке нет такого товара!'})
                continue

            if store.total_num_pieces < item['quantity']:
                errors.append({
                    'global_item': global_item.name,
                    'quantity': 'В аптеке недостаточное количество товара!'
                })
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        client_ordered_items = validated_data.pop("client_ordered_items", None)
        client_order = ClientOrder.objects.create(**validated_data,
                                                  store=validated_data.get('cashier').store,
                                                  date_ordered=datetime.now())
        for item_params in client_ordered_items:
            client_ordered_item = ClientOrderedItem.objects.create(client_order=client_order, **item_params)
            store_item = StoreItem.objects.get(global_item=client_ordered_item.global_item)
            store_item.quantity -= client_ordered_item.quantity
            store_item.save()
        return client_order


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
