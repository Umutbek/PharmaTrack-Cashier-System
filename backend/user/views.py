from item.serializers import CashierWorkShiftSerializer
from item.services import end_work_shift
from item.services import get_active_cashier_work_shift
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from user.models import Cashier, Manager
from user.serializers import (CashierSerializer, ManagerSerializer,
                              TokenObtainPairWithUserInfoSerializer,
                              TokenRefreshWithUserInfoSerializer)


class CashierViewSet(viewsets.ModelViewSet):
    serializer_class = CashierSerializer
    queryset = Cashier.objects.all()

    @action(detail=True, methods=['GET'])
    def active_work_shift(self, request, pk=None):
        current_cashier = self.get_object()
        work_shift = get_active_cashier_work_shift(current_cashier)
        serializer = CashierWorkShiftSerializer(work_shift)
        return Response(serializer.data)


class ManagerViewSet(viewsets.ModelViewSet):
    serializer_class = ManagerSerializer
    queryset = Manager.objects.all()


class Login(TokenObtainPairView):
    serializer_class = TokenObtainPairWithUserInfoSerializer
    permission_classes = [AllowAny, ]


class Logout(APIView):
    def post(self, request):
        if request.user.is_anonymous:
            return Response({'detail': 'User is already anonymous'},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.user.cashier:
            end_work_shift(request.user.cashier)
        return Response(status=status.HTTP_200_OK)


class CurrentUser(APIView):
    def get(self, request):
        serializer = CashierSerializer(request.user)
        return Response(serializer.data)


class RefreshUserInfo(TokenRefreshView):
    serializer_class = TokenRefreshWithUserInfoSerializer
    permission_classes = [AllowAny, ]
