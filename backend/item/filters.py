from item.models import (Category, GlobalItem, StoreOrder, ClientOrderedItem, StoreOrderItem, StoreItem)
from django_filters import FilterSet
from django_filters import rest_framework as filters


class GlobalItemFilter(FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    category = filters.NumberFilter('category')
    unique_id = filters.CharFilter('unique_id')

    class Meta:
        models = GlobalItem
        fields = ('name', 'category', 'unique_id')


class StoreOrderFilter(FilterSet):
    store = filters.CharFilter('store')
    depot = filters.CharFilter('depot')
    status = filters.NumberFilter('status')

    class Meta:
        models = StoreOrder
        fields = ('store', 'depot', 'status')


class StoreOrderItemFilter(FilterSet):
    order = filters.CharFilter('item')

    class Meta:
        models = StoreOrderItem
        fields = ('order',)


class ClientOrderedItemFilter(FilterSet):
    date_from = filters.DateFilter(field_name="date", lookup_expr='gte')
    date_to = filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        models = ClientOrderedItem
        fields = ('date_from', 'date_to')