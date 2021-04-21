from item.constants import StoreOrderStatuses
from rest_framework.response import Response
from rest_framework import status


def check_store_order_status(func):
    def wrapped(self, request, pk=None):
        store_order = self.get_object()
        if store_order.status in [StoreOrderStatuses.COMPLETED, StoreOrderStatuses.DECLINED]:
            return Response(
                {'detail': 'Нельзя менять завершенные или отказанные заказы'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return func(self, request, pk)

    return wrapped
