from rest_framework import serializers
from core import models

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for category"""
    class Meta:
        model = models.Category
        fields = ('id', 'name', 'storeid', 'totalCost', 'totalQuantity')
        read_only_fields = ('id',)


class GlobalItemSerializer(serializers.ModelSerializer):
    """Serializer for Item"""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.GlobalItem
        fields = (
            'id', 'uniqueid', 'name', 'producer', 'category', 'image', 'description'
        )


class FarmStoreItemsSerializer(serializers.ModelSerializer):
    """Serializer for farmstoreitems Item"""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.FarmStoreItems
        fields = (
            'id', 'globalitem', 'seria', 'sepparts', 'deadline', 'cost'
        )


class GetFarmStoreItemsSerializer(serializers.ModelSerializer):
    """Serializer for farmstoreitems Item"""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.FarmStoreItems
        fields = (
            'id', 'globalitem', 'seria', 'sepparts', 'deadline', 'cost'
        )
        depth=1


class AddStoreItemSerializer(serializers.ModelSerializer):
    """Serializer for adding item to store"""
    class Meta:
        model = models.AddStoreItem
        fields = (
            'id', 'uniqueid', 'seria', 'sepparts', 'quantity', 'storeid'
        )
        read_only_fields = ('id',)


class ItemSerializer(serializers.ModelSerializer):
    """Serializer for Item active"""

    class Meta:
        model = models.Item
        fields = (
            'id', 'farmstoreitems', 'quantity', 'parts',
            'costsale', 'issale', 'totalcost', 'storeid'
        )
        read_only_fields = ('id',)
        depth=2


class ItemPostSerializer(serializers.ModelSerializer):
    """Serializer for Item active"""
    id = serializers.IntegerField(required=False)

    class Meta:
        model = models.Item
        fields = (
            'id', 'farmstoreitems', 'quantity', 'parts'
            'costsale', 'issale', 'totalcost', 'storeid'
        )


class StoreOrderDetailSerializer(serializers.ModelSerializer):
    """Serializer for store order"""

    class Meta:
        model = models.StoreOrder
        fields = (
            'id', 'farmstoreitems', 'quantity'
        )
        read_only_fields = ('id',)
        depth=1


class StoreOrderSerializer(serializers.ModelSerializer):
    """Serializer for store order"""

    class Meta:
        model = models.StoreOrder
        fields = (
            'id', 'farmstoreitems', 'quantity'
        )
        read_only_fields = ('id',)
        depth=1


class ItemsInSerializer(serializers.ModelSerializer):
    """Serializer for store order"""
    storeorderitem = StoreOrderSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = models.ItemsIn
        fields = (
            'id', 'storeorderitem', 'uniqueid', 'address', 'datesent', 'storedepotid', 'depotid', 'totalCount', 'totalCost', 'status', 'iseditable'
        )
        read_only_fields = ('id', 'uniqueid', 'datereceived', 'totalCount', 'totalCost', 'status', 'iseditable')

    def create(self, validated_data):
        storeorderitem = validated_data.pop("storeorderitem", None)
        itemin = models.ItemsIn.objects.create(**validated_data)
        if storeorderitem:
            for i in storeorderitem:
                models.StoreOrder.objects.create(itemin=itemin, **i)
        return itemin


class GetItemsInSerializer(serializers.ModelSerializer):
    """Serializer for store order"""
    storeorderitem = StoreOrderSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = models.ItemsIn
        fields = (
            'id', 'storeorderitem', 'address', 'datesent', 'storedepotid', 'depotid', 'status', 'iseditable'
        )
        read_only_fields = ('id', 'iseditable')
        depth=1


class OrderIdSerializer(serializers.ModelSerializer):
    """Serializer for get order id"""
    class Meta:
        model = models.OrderReceived

        fields = (
            'id', 'orderid'
        )
        read_only_fields = ('id',)


class ClientItemOrderSerializer(serializers.ModelSerializer):
    """Serializer for client order"""

    class Meta:
        model = models.ClientOrderItem
        fields = (
            'id', 'farmstoreitems', 'quantity', 'sepparts', 'date', 'costone', 'costtotal'
        )
        read_only_fields = ('id',)


class ClientOrderSerializer(serializers.ModelSerializer):
    """Serializer for client order"""
    clientorder = ClientItemOrderSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = models.ClientOrder
        fields = (
            'id', 'clientorder', 'datetime', 'cashier', 'countitem', 'total'
        )
        read_only_fields = ('id',)

    def create(self, validated_data):

        clientorder = validated_data.pop("clientorder", None)
        transactionid = models.ClientOrder.objects.create(**validated_data)

        if clientorder:
            for i in clientorder:
                models.ClientOrderItem.objects.create(transactionid=transactionid, **i)

        return transactionid


class ClientOrderIdSerializer(serializers.ModelSerializer):
    """Serializer for get client order id"""
    class Meta:
        model = models.OrderReceivedClient

        fields = (
            'id', 'clientorderid'
        )
        read_only_fields = ('id',)


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for store order"""

    class Meta:
        model = models.Report
        fields = (
            'id', 'datefrom', 'dateto', 'inTotal', 'incomeTotal', 'earnTotal'
        )
        read_only_fields = ('id', 'inTotal', 'incomeTotal', 'earnTotal')
