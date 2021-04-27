import logging

from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from django_fsm import TransitionNotAllowed
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from item import serializers
from item.constants import StoreOrderStatuses
from item.filters import (ClientOrderedItemFilter, GlobalItemFilter,
                          StoreOrderFilter, StoreItemFilter)
from item.models import (ClientOrderedItem, CashierWorkShift, GlobalItem,
                         Category, ClientOrder, StoreOrder, StoreItem,
                         StoreOrderItem, Store, Depot, StoreOrderHistory)
from item.serializers import StoreSerializer, DepotSerializer

logger = logging.getLogger(__name__)


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


class StoreItemView(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    serializer_class = serializers.StoreItemSerializer
    queryset = StoreItem.objects.all()
    lookup_field = 'global_item__unique_id'
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreItemFilter

    def get_queryset(self):
        store_id = self.kwargs.get('storeId', None)
        return StoreItem.objects.filter(store=store_id)


class StoreOrderHistoryView(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            GenericViewSet):
    serializer_class = serializers.StoreOrderHistorySerializer
    queryset = StoreOrderHistory.objects.all()

    def get_queryset(self):
        store_order_id = self.kwargs.get('storeOrderId', None)
        return StoreOrderHistory.objects.filter(store_order=store_order_id)


class StoreOrderView(ModelViewSet):
    serializer_class = serializers.StoreOrderSerializer
    serializer_class_extended = serializers.StoreOrderSerializerExtended
    queryset = StoreOrder.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreOrderFilter

    @action(detail=True, methods=['GET'])
    def as_html(self, request, pk=None):
        store_order = StoreOrder.objects.filter(pk=pk).prefetch_related('store_ordered_items').first()
        return render(request, 'store-order.html', {'store_order': store_order})

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        target = request.data.get('status')
        # проверяем, можно ли обновить данный заказ
        try:
            if target == StoreOrderStatuses.NEW:
                instance.update_new()
            elif target == StoreOrderStatuses.SENT:
                instance.send()
            elif target == StoreOrderStatuses.DELIVERED:
                instance.deliver()
            else:
                return Response({'type': 'update_fail',
                                 'detail': 'Invalid update status',
                                 'store_order': self.get_serializer(instance).data,
                                 }, status=status.HTTP_400_BAD_REQUEST)
        except TransitionNotAllowed as e:
            return Response({'type': 'update_fail',
                             'detail': str(e),
                             'store_order': self.get_serializer(instance).data,
                             }, status=status.HTTP_400_BAD_REQUEST)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'type': 'update_success',
                         'detail': 'Successfully updated!',
                         'store_order': serializer.data})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        as_html = bool(self.request.query_params.get('as_html', False))
        if as_html:
            return self.as_html(request, serializer.data.get('id'))
        else:
            return Response(serializer.data)


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
