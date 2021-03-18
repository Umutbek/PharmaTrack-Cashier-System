from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.generics import ListAPIView
from django.shortcuts import render
from item import serializers
from core import models
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters import FilterSet
from django_filters import rest_framework as filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from item.pagination import PaginationHandlerMixin
import datetime
from dateutil.relativedelta import relativedelta


class CategoryFilter(FilterSet):
    """Filter for an item"""
    storeid = filters.CharFilter('storeid')
    class Meta:
        models = models.Category
        fields = ('storeid')


class GetCategoryView(ListAPIView):

    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = CategoryFilter


class CategoryView(APIView):
    """API view for category list"""
    serializer_class = serializers.CategorySerializer

    def post(self, request):
        """Create new category"""
        serializer = serializers.CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class GlobalItemView(APIView, PaginationHandlerMixin):
    """API view for global item list"""
    serializer_class = serializers.GlobalItemSerializer

    def get(self, request):
        """Return list of clinet order"""
        globalitem = models.GlobalItem.objects.all()
        serializer = serializers.GlobalItemSerializer(globalitem, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create new itemglobal"""
        serializer = serializers.GlobalItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class FarmStoreItemsView(APIView, PaginationHandlerMixin):
    """API view for farm store item list"""
    serializer_class = serializers.FarmStoreItemsSerializer

    def get(self, request):
        """Return list of clinet order"""
        farmstoreitems = models.FarmStoreItems.objects.all()
        serializer = serializers.FarmStoreItemsSerializer(farmstoreitems, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create new itemglobal"""
        serializer = serializers.FarmStoreItemsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class ItemFilter(FilterSet):
    """Filter for an item"""
    storeid = filters.CharFilter('storeid')
    category = filters.CharFilter('farmstoreitems__globalitem__category')
    uniqueid = filters.CharFilter('farmstoreitems__globalitem__uniqueid')

    class Meta:
        models = models.Item
        fields = ('storeid', 'category', 'uniqueid')


class ActiveItemsView(ListAPIView):
    """View for Active items"""
    serializer_class = serializers.ItemSerializer
    queryset = models.Item.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ItemFilter


class PostItemView(APIView):
    """API view for category list"""
    serializer_class = serializers.ItemPostSerializer

    def post(self, request):
        """Create new category"""
        serializer = serializers.ItemPostSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class UpdateItemsView(generics.RetrieveUpdateDestroyAPIView):
    """Create new user in system"""
    serializer_class = serializers.ItemSerializer
    queryset = models.Item.objects.all()


class AddStoreItemView(APIView):
    """API view for client order list"""
    serializer_class = serializers.AddStoreItemSerializer

    def post(self, request):
        """Create new store order"""
        serializer = serializers.AddStoreItemSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            farmstore = models.FarmStoreItems.objects.get(globalitem__uniqueid=saved_data.uniqueid) & models.FarmStoreItems.objects.get(seria=saved_data.seria)
            if farmstore:
                item = models.Item.objects.filter(farmstoreitems=farmstore.id) & models.Item.objects.filter(storeid=saved_data.storeid)
                if item:
                    for i in item:
                        i.quantity = i.quantity + saved_data.quantity
                        i.parts = i.parts + saved_data.sepparts
                        i.save()
                        saved_data.delete()
                else:
                    active = models.Item(
                        farmstoreitems = farmstore, quantity = saved_data.quantity, parts = saved_data.sepparts,
                        storeid=saved_data.storeid
                    )
                    active.save()
                    saved_data.delete()
                return Response(serializer.data)

            else:
                return Response({'Success':False})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class ItemsInView(APIView):
    """API view for store order list"""
    serializer_class = serializers.ItemsInSerializer

    def post(self, request):
        """Create new store order"""
        serializer = serializers.ItemsInSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            saved_data.uniqueid = saved_data.id * 11111
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
                )

class ItemsInDetailView(APIView):
    serializer_class = serializers.ItemsInSerializer

    def get(self, request, pk):
        """Return a list of category details"""
        item = models.ItemsIn.objects.get(pk=pk)
        b = item.datesent
        a = datetime.datetime.now()

        if b.day < a.day or b.month < a.month:
            item.iseditable = False

        serializer = serializers.ItemsInSerializer(item)
        return Response(serializer.data)


class ItemsInFilter(FilterSet):
    """Filter for an item"""
    storeid = filters.CharFilter('storedepotid')
    depotid = filters.CharFilter('depotid')

    class Meta:
        models = models.ItemsIn
        fields = ('storeid', 'depotid')


class GetItemsInView(ListAPIView):
    """API view for client selected items"""
    serializer_class = serializers.GetItemsInSerializer
    queryset = models.ItemsIn.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ItemsInFilter


class StoreOrderDetailView(APIView):
    """API view for client order list"""
    serializer_class = serializers.ItemsInSerializer

    def get(self, request, pk):
        """Return list of clinet order"""
        storeorder = models.ItemsIn.objects.get(pk=pk)
        serializer = serializers.ItemsInSerializer(storeorder)
        storeitem = models.StoreOrder.objects.filter(itemin=pk)
        count = 0
        count1 = 0
        for i in storeitem:
            i.costTotal = i.quantity * i.cost
            count = count + i.costTotal
            count1 = count1 + 1
            i.save()
        storeorder.totalCost = count
        storeorder.totalCount = count1
        storeorder.save()

        context = {'storeorder': storeorder, 'storeitem':storeitem}
        return render(request, 'storeorder.html', context)


class ItemFilter(FilterSet):
    """Filter for an item"""
    order = filters.CharFilter('itemin')

    class Meta:
        models = models.StoreOrder
        fields = ('order',)


class GetOrderView(ListAPIView):
    """API view for client selected items"""
    serializer_class = serializers.StoreOrderDetailSerializer
    queryset = models.StoreOrder.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ItemFilter


class OrderIdView(APIView):
    """API view for global item list"""
    serializer_class = serializers.OrderIdSerializer

    def post(self, request):
        """Send id of order to change status"""
        serializer = serializers.OrderIdSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            itemsin = models.ItemsIn.objects.get(id=saved_data.orderid.id)
            order = models.StoreOrder.objects.filter(itemin=itemsin.id)

            if itemsin and order:
                for i in order:
                    activeitems = models.Item.objects.filter(farmstoreitems=i.farmstoreitems.id) & models.Item.objects.filter(storeid__type=1)
                    if activeitems:
                        for j in activeitems:
                            j.quantity = j.quantity + i.quantity
                            j.parts = j.parts + i.farmstoreitems.sepparts
                            j.save()
                            itemsin.status = True
                            itemsin.save()
                            break
                    else:
                        itemsin.status = True
                        check = models.Item.objects.all()
                        if check:
                            max = models.Item.objects.all().order_by("-id")[0]
                            active = models.Item(
                                id=max.id+1, farmstoreitems = i.farmstoreitems, quantity = i.quantity, parts= i.farmstoreitems.sepparts,
                                storeid=itemsin.storedepotid
                            )
                            active.save()
                            itemsin.save()
                        else:
                            active = models.Item(
                                id=1, farmstoreitems = i.farmstoreitems, quantity = i.quantity, parts= i.farmstoreitems.sepparts,
                                storeid=itemsin.storedepotid
                            )
                            active.save()
                            itemsin.save()

            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class ClientOrderView(APIView):
    """API view for client order list"""
    serializer_class = serializers.ClientOrderSerializer

    def post(self, request):
        """Create new store order"""
        serializer = serializers.ClientOrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class ClientItemFilter(FilterSet):
    """Filter for an item"""
    datefrom = filters.DateFilter(field_name="date",lookup_expr='gte')
    dateto = filters.DateFilter(field_name="date",lookup_expr='lte')

    class Meta:
        models = models.ClientOrderItem
        fields = ('datefrom', 'dateto')

class ClientItemOrderView(ListAPIView):
    """API view for client selected items"""
    serializer_class = serializers.ClientItemOrderSerializer
    queryset = models.ClientOrderItem.objects.all()

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_class = ClientItemFilter


class ClientOrderDetailView(APIView):
    """API view for client order list"""
    serializer_class = serializers.ClientOrderSerializer

    def get(self, request, pk):
        """Return list of clinet order"""
        clientorder = models.ClientOrder.objects.get(pk=pk)
        serializer = serializers.ClientOrderSerializer(clientorder)
        clientitem = models.ClientOrderItem.objects.filter(transactionid=pk)
        count = 0
        count1 = 0
        for i in clientitem:
            i.costtotal = i.quantity * i.costone
            count = count + i.costtotal
            count1 = count1 + 1
            i.save()
        clientorder.total = count
        clientorder.countitem = count1
        clientorder.save()

        context = {'clientorder':clientorder,'clientitem':clientitem}
        return render(request, 'index.html', context)


class ClientOrderIdView(APIView):
    """API view for send client order id, to know is order received"""
    serializer_class = serializers.ClientOrderIdSerializer
    def post(self, request):
        """Send id of client order to change status"""
        serializer = serializers.ClientOrderIdSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            clientorder = models.ClientOrder.objects.get(id=saved_data.clientorderid.id)
            order = models.ClientOrderItem.objects.filter(transactionid=clientorder.id)

            if clientorder and order:
                for i in order:
                    activeitems = models.Item.objects.filter(farmstoreitems=i.farmstoreitems.id)
                    if activeitems:
                        for j in activeitems:
                            j.quantity = (j.quantity - i.quantity) - (i.sepparts/j.parts)
                            print("i Sepparts", i.sepparts)
                            print("j Sepparts", j.parts)
                            print("Delete", i.sepparts/j.parts)
                            j.parts = j.parts - i.sepparts
                            print("i quantity", i.quantity)
                            j.save()
                            clientorder.status = True
                            clientorder.save()
                            return Response({"Success":True})
                    else:
                        return Response({"Success":False})
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class ReportView(APIView):
    """API view for client order list"""
    serializer_class = serializers.ReportSerializer

    def post(self, request):
        """Create new store order"""
        serializer = serializers.ReportSerializer(data=request.data)
        if serializer.is_valid():
            saved_data = serializer.save()
            count=0
            items = models.ClientOrderItem.objects.filter(date__range=[saved_data.datefrom, saved_data.dateto])
            if items:
                for i in items:
                    count = count + i.total
                saved_data.incomeTotal = count
                saved_data.earnTotal = saved_data.incomeTotal-saved_data.inTotal
                saved_data.save()
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
