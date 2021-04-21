from item.models import (GlobalItem,
                         Category, StoreItem, Store, Depot,
                         StoreOrder, ClientOrderedItem, ClientOrder,
                         CashierWorkShift, Report, StoreOrderItem)
from rest_framework import serializers


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
        fields = ('id', 'name', 'store', 'total_cost', 'total_quantity')
        extra_kwargs = {
            'total_cost': {'read_only': True},
            'total_quantity': {'read_only': True},
        }


class GlobalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalItem
        fields = ('id', 'unique_id', 'name', 'producer', 'category', 'image',
                  'description', 'series', 'sepparts', 'expiration_date', 'price_selling')


class StoreItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItem
        fields = ('id', 'global_item', 'quantity', 'parts',
                  'price_sale', 'is_sale', 'total_cost', 'store')
        depth = 2


class StoreOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreOrderItem
        fields = ('store_order', 'global_item', 'quantity', 'cost_total')


class StoreOrderSerializer(serializers.ModelSerializer):
    store_order_items = StoreOrderItemSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = StoreOrder
        depth = 1
        fields = ('id', 'unique_id', 'store_order_items', 'depot', 'store', 'address',
                  'date_sent', 'date_received', 'status', 'is_editable')
        extra_kwargs = {
            'date_received': {'read_only': True},
            'is_editable': {'read_only': True}
        }
        # todo: date_received should automatically set
        # todo: can't edit if is_editable false
        # todo: determine what status could be

    def create(self, validated_data):
        store_order_items = validated_data.pop("store_order_items", None)
        store_order = StoreOrder.objects.create(**validated_data)

        for item in store_order_items:
            StoreOrder.objects.create(store_order=store_order, **item)
        return store_order


class ClientOrderedItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientOrderedItem
        fields = ('id', 'global_item', 'quantity', 'sepparts',
                  'date_ordered', 'cost_one', 'cost_total')
        read_only_fields = ('id',)


class ClientOrderSerializer(serializers.ModelSerializer):
    client_ordered_items = ClientOrderedItemSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = ClientOrder
        fields = ('id', 'client_ordered_items', 'date_ordered', 'cashier',
                  'count_item', 'total_sum')

    def create(self, validated_data):
        client_ordered_items = validated_data.pop("client_ordered_items", None)
        client_order = ClientOrder.objects.create(**validated_data)

        for item in client_ordered_items:
            ClientOrderedItem.objects.create(client_order=client_order, **item)

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
