from django_filters import FilterSet
from django_filters import rest_framework as filters

from user.models import Client


class ClientFilter(FilterSet):
    type = filters.NumberFilter(field_name='type')

    class Meta:
        models = Client
        fields = ('type',)