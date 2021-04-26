import logging
from datetime import datetime
from django_fsm import TransitionNotAllowed
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
from item.constants import StoreOrderStatuses

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


class StoreOrderView(ModelViewSet):
    serializer_class = serializers.StoreOrderSerializer
    queryset = StoreOrder.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreOrderFilter

    @action(detail=True, methods=['GET'])
    def as_html(self, request, pk=None):
        store_order = StoreOrder.objects.filter(pk=pk).prefetch_related('store_ordered_items').first()
        return render(request, 'store-order.html', {'store_order': store_order})

    @action(detail=True, methods=['PUT'])
    def status_update(self, request, pk=None):
        logger.info(pk)
        store_order = StoreOrder.objects.get(id=pk)
        target = int(request.query_params.get('status'))
        additional_info = {}
        try:
            if target == StoreOrderStatuses.SENT:
                store_order.send()
                additional_info['detail'] = 'Status updated successfully!'
            elif target == StoreOrderStatuses.DELIVERED:
                store_order.deliver()
                store_items = self.save_delivered_items(store_order)
                additional_info['updated_items'] = StoreItemSerializer(store_items, many=True).data
                additional_info['detail'] = 'Items added successfully!'
            else:
                return Response({'type': 'update_fail',
                                 'detail': 'Invalid update status',
                                 'store_order': serializers.StoreOrderSerializer(store_order).data,
                                 }, status=status.HTTP_400_BAD_REQUEST)
        except TransitionNotAllowed as e:
            return Response({'type': 'update_fail',
                             'detail': str(e),
                             'store_order': serializers.StoreOrderSerializer(store_order).data,
                             }, status=status.HTTP_400_BAD_REQUEST)
        store_order.status = target
        store_order.save()
        return Response({
            'store_order': serializers.StoreOrderSerializer(store_order).data,
            **additional_info
        }, status=status.HTTP_202_ACCEPTED)

    def save_delivered_items(self, store_order):
        updated_items = []
        for item in store_order.store_ordered_items.all():
            store_item = StoreItem.objects.get(store=store_order.store,
                                               global_item=item.global_item)
            total_num_pieces = store_item.total_num_pieces + item.total_num_pieces
            store_item.quantity = total_num_pieces // store_item.global_item.max_num_pieces
            store_item.num_pieces = total_num_pieces % store_item.global_item.max_num_pieces
            store_item.save()
            updated_items.append(store_item)

        return updated_items

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.as_html(request, serializer.data.get('id'))


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
