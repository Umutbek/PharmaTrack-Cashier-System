from django.urls import path, include
from item import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('categories', views.CategoryView)
router.register('global-items', views.GlobalItemView)
router.register('store-orders', views.StoreOrderView)
router.register('store-ordered-items', views.StoreOrderItemView)
router.register('client-orders', views.ClientOrderView)
router.register('client-ordered-items', views.ClientOrderedItemView)
router.register('cashier-work-shifts', views.CashierWorkShiftView)
router.register('stores', views.StoreViewSet)
router.register(r'stores/(?P<storeId>[^/.]+)/items', views.StoreItemView)
router.register('depots', views.DepotViewSet)


app_name = 'item'
urlpatterns = [
    path('', include(router.urls))
]
