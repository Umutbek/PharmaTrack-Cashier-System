from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from item import serializers
from item.decorators import check_store_order_status
from item.filters import (CategoryFilter, ClientOrderedItemFilter, GlobalItemFilter,
                          StoreOrderFilter)
from item.models import (ClientOrderedItem, CashierWorkShift, GlobalItem,
                         Category, ClientOrder, StoreOrder, StoreItem,
                         StoreOrderItem, Store, Depot)
from item.serializers import StoreSerializer, DepotSerializer
from rest_framework import mixins
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet


class StoreViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()


class DepotViewSet(ModelViewSet):
    serializer_class = DepotSerializer
    queryset = Depot.objects.all()


class CategoryView(ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = CategoryFilter


class GlobalItemView(ModelViewSet):
    serializer_class = serializers.GlobalItemSerializer
    queryset = GlobalItem.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = GlobalItemFilter


class StoreItemView(ModelViewSet):
    serializer_class = serializers.StoreItemSerializer
    queryset = StoreItem.objects.all()


class StoreOrderView(ModelViewSet):
    serializer_class = serializers.StoreOrderSerializer
    queryset = StoreOrder.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreOrderFilter

    @check_store_order_status
    def update(self, request, pk=None):
        return super(StoreOrderView, self).update(request, pk)

    @check_store_order_status
    def partial_update(self, request, pk=None):
        return super(StoreOrderView, self).partial_update(request, pk)


class StoreOrderItemView(ModelViewSet):
    serializer_class = serializers.StoreOrderItemSerializer
    queryset = StoreOrderItem.objects.all()

    def retrieve(self, request, pk=None):
        store_order = self.get_object()
        store_order_items = StoreOrderItem.objects.filter(itemin=pk)
        total_cost = 0
        for item in store_order_items:
            item.cost_total = item.quantity * item.cost
            total_cost = total_cost + item.cost_total
            item.save()
        store_order.total_cost = total_cost
        store_order.total_cnt = len(store_order_items)
        store_order.save()

        context = {'store_order': store_order, 'store_order_items': store_order_items}
        return render(request, 'store-order.html', context)


class ClientOrderView(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      # mixins.UpdateModelMixin,
                      # mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    serializer_class = serializers.ClientOrderSerializer
    queryset = ClientOrder.objects.all()

    def retrieve(self, request, pk=None):
        client_order = ClientOrder.objects.get(pk=pk)
        client_ordered_items = client_order.client_ordered_items.all()
        total_sum = 0
        for item in client_ordered_items:
            item.cost_total = item.quantity * item.cost_one
            total_sum = total_sum + item.costtotal
            # item.save()
        client_order.total_sum = total_sum
        client_order.count_item = len(client_ordered_items)
        # client_order.save()

        context = {'client_order': client_order, 'client_ordered_items': client_ordered_items}
        return render(request, 'client-order.html', context)


class ClientOrderedItemView(ModelViewSet):
    serializer_class = serializers.ClientOrderedItemSerializer
    queryset = ClientOrderedItem.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ClientOrderedItemFilter


class CashierWorkShiftView(ModelViewSet):
    serializer_class = serializers.CashierWorkShiftSerializer
    queryset = CashierWorkShift.objects.all()
