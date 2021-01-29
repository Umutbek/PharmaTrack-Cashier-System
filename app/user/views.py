from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from core import models


class CreateUserView(generics.CreateAPIView):
    """Create new user in system"""
    serializer_class = serializers.UserSerializer


class CreateTokenView(APIView):
    """Create a new auth token for user"""
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        info = models.User.objects.filter(login=user)
        serializer1 = serializers.UserSerializer(info, many=True)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, 'data': serializer1.data})


class CreateCashierView(APIView):
    """Create new user in system"""
    serializer_class = serializers.CashierSerializer

    def post(self, request):
        """Create new user"""
        serializer = serializers.CashierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class CheckUsernameView(APIView):
    serializer_class = serializers.CheckSerializer

    def post(self, request):
        """Check Username"""
        serializer = serializers.CheckSerializer(data=request.data)

        if serializer.is_valid():
            saved_data = serializer.save()
            check = models.User.objects.filter(username=saved_data)
            if check:
                for i in check:
                    saved_data.delete()
                    return Response({'Success': True})
                    break
            else:
                saved_data.delete()
                return Response({'Success': False})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckPhoneView(APIView):
    serializer_class = serializers.CheckSerializer

    def post(self, request):
        """Check Phone"""
        serializer = CheckSerializer(data=request.data)

        if serializer.is_valid():
            saved_data = serializer.save()
            check = Cashier.objects.filter(phone=saved_data.username)
            if check:
                for i in check:
                    saved_data.delete()
                    return Response({'Success': True})
                    break
            else:
                saved_data.delete()
                return Response({'Success': False})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashierLoginView(APIView):
    serializer_class = serializers.CashierLoginSerializer

    def post(self, request):
        """Login cashier"""
        serializer = serializers.CashierLoginSerializer(data=request.data)

        if serializer.is_valid():
            saved_data = serializer.save()
            login = models.Cashier.objects.filter(phone=saved_data.phone) & models.Cashier.objects.filter(password=saved_data.password)

            if login:
                for i in login:
                    finish = models.FinishCashier(
                        datestart=saved_data.lastdate
                    )
                    finish.save()

                    i.finishdayid = finish.id
                    i.lastdate=saved_data.lastdate
                    i.save()
                    serializer1 = serializers.CashierSerializer(login, many=True)
                    saved_data.delete()
                    return Response(serializer1.data)
                    break
            else:
                saved_data.delete()
                return Response(['Wrong Phone or password'])
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FinishCashierView(APIView):
    """API view for finish cashier list"""
    serializer_class = serializers.FinishCashierSerializer

    def get(self, request):
        """Return list of clinet order"""
        finishcashier = models.FinishCashier.objects.all()
        serializer = serializers.FinishCashierSerializer(finishcashier, many=True)
        return Response(serializer.data)


class CashierIDView(APIView):
    """API view for send cashier id list"""
    serializer_class = serializers.CashierIDSerializer

    def post(self, request):
        """Send cashier id"""
        serializer = serializers.CashierIDSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            finishday = models.FinishCashier.objects.get(pk=saved_data.finishdayid)
            finishday.dateend = saved_data.datetime
            finishday.cashier = saved_data.cashierid
            transactions = models.ClientOrder.objects.filter(datetime__range=[finishday.datestart, finishday.dateend]) & models.ClientOrder.objects.filter(cashier=saved_data.cashierid)
            if transactions:
                for i in transactions:
                    finishday.transactions.add(i)
            finishday.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class StoreDepotFilter(FilterSet):
    """Filter for an item"""
    type = filters.CharFilter('type')

    class Meta:
        models = models.User
        fields = ('type')


class GetStoreDepotView(ListAPIView):
    serializer_class = serializers.UserSerializer
    queryset = models.User.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = StoreDepotFilter
