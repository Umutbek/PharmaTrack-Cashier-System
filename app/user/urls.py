from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('registerstore/', views.CreateUserView.as_view(), name='create'),
    path('registercashier/', views.CreateCashierView.as_view(), name='createcashier'),

    path('getstoreordepot/', views.GetStoreDepotView.as_view()),

    path('loginstore/', views.CreateTokenView.as_view(), name='token'),
    path('logincashier/', views.CashierLoginView.as_view()),

    path('finishcashier/', views.FinishCashierView.as_view()),
    path('sendcashierid/', views.CashierIDView.as_view()),

    path('checkusername/', views.CheckUsernameView.as_view()),
    path('checkphone/', views.CheckPhoneView.as_view()),
]
