from item.models import (Category, GlobalItem, StoreOrder, ClientOrderedItem, StoreOrderItem)
from django_filters import FilterSet
from django_filters import rest_framework as filters


class CategoryFilter(FilterSet):
    storeid = filters.CharFilter('store')

    class Meta:
        models = Category
        fields = ('store', )


class GlobalItemFilter(FilterSet):
    store = filters.CharFilter('store')
    category = filters.CharFilter('category')
    unique_id = filters.CharFilter('unique_id')

    class Meta:
        models = GlobalItem
        fields = ('store', 'category', 'unique_id')


class StoreOrderFilter(FilterSet):
    store = filters.CharFilter('store')
    depot = filters.CharFilter('depot')

    class Meta:
        models = StoreOrder
        fields = ('store', 'depot')


class StoreOrderItemFilter(FilterSet):
    order = filters.CharFilter('item')

    class Meta:
        models = StoreOrderItem
        fields = ('order',)


class ClientOrderedItemFilter(FilterSet):
    date_from = filters.DateFilter(field_name="date",lookup_expr='gte')
    date_to = filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        models = ClientOrderedItem
        fields = ('date_from', 'date_to')