from datetime import datetime

from django.db import transaction
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from item import serializers
from item.filters import (ClientOrderedItemFilter, GlobalItemFilter,
                          StoreOrderFilter, StoreItemFilter)
from item.models import (ClientOrderedItem, CashierWorkShift, GlobalItem,
                         Category, ClientOrder, StoreOrder, StoreItem,
                         StoreOrderItem, Store, Depot)
from item.serializers import StoreSerializer, DepotSerializer, StoreItemSerializer


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


class GlobalItemView(ModelViewSet):
    serializer_class = serializers.GlobalItemSerializer
    queryset = GlobalItem.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = GlobalItemFilter


class StoreItemView(ModelViewSet):
    serializer_class = serializers.StoreItemSerializer
    queryset = StoreItem.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreItemFilter


class StoreOrderView(ModelViewSet):
    serializer_class = serializers.StoreOrderSerializer
    queryset = StoreOrder.objects.filter(next__isnull=True)
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreOrderFilter

    @action(detail=True, methods=['GET'])
    def as_html(self, request, pk=None):
        store_order = StoreOrder.objects.filter(pk=pk).prefetch_related('store_ordered_items').first()
        return render(request, 'store-order.html', {'store_order': store_order})

    @transaction.atomic
    @action(detail=True, methods=['UPDATE'])
    def confirm(self, request, pk=None):
        store_order = self.get_object()

        store_ordered_items = store_order.store_ordered_items.all()
        updated_items, created_items = [], []
        added_items_qt = 0
        for item in store_ordered_items:
            try:
                store_item = StoreItem.objects.get(store=store_order.store,
                                                   global_item=item.global_item)
                updated_items.append(store_item)
            except StoreItem.DoesNotExist:
                store_item = StoreItem.objects.create(
                    store=store_order.store,
                    global_item=item.global_item,
                    quantity=0,
                    price_sale=item.global_item.price_selling
                )
                created_items.append(store_item)
            store_item.quantity += item.quantity
            added_items_qt += item.quantity
            store_item.save()

        actual_items_qt = sum(store_ordered_items.values_list('quantity', flat=True))
        if added_items_qt != actual_items_qt:
            return Response({
                'added_items_qt': added_items_qt,
                'actual_items_qt': actual_items_qt,
                'detail': 'Что-то пошло не так. Не все товары были добавлены.'
            }, status=status.HTTP_400_BAD_REQUEST)

        store_order.date_received = datetime.now()
        store_order.is_editable = False
        store_order.save()
        return Response({
            'detail': 'Отлично! Все товары были добавлены',
            'updated_items': StoreItemSerializer(updated_items, many=True).data,
            'created_items': StoreItemSerializer(created_items, many=True).data,
            'added_items_qt': added_items_qt
        }, status=status.HTTP_202_ACCEPTED)


class StoreOrderItemView(mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    serializer_class = serializers.StoreOrderItemSerializer
    queryset = StoreOrderItem.objects.all()


class ClientOrderView(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      # mixins.UpdateModelMixin,
                      # mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    serializer_class = serializers.ClientOrderSerializer
    queryset = ClientOrder.objects.all()

    @action(detail=True, methods=['GET'])
    def as_html(self, request, pk=None):
        client_order = ClientOrder.objects.filter(pk=pk).prefetch_related('client_ordered_items').first()
        return render(request, 'client-order.html', {'client_order': client_order})


class ClientOrderedItemView(ModelViewSet):
    serializer_class = serializers.ClientOrderedItemSerializer
    queryset = ClientOrderedItem.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ClientOrderedItemFilter


class CashierWorkShiftView(ModelViewSet):
    serializer_class = serializers.CashierWorkShiftSerializer
    queryset = CashierWorkShift.objects.all()
