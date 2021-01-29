from django.urls import path
from user import views

app_name = 'user'

urlpatterns = [
    path('register/', views.CreateUserView.as_view(), name='create'),
    path('registercashier/', views.CreateCashierView.as_view(), name='createcashier'),

    path('getstoredepot/', views.GetStoreDepotView.as_view()),

    path('login/', views.CreateTokenView.as_view(), name='token'),
    path('logincashier/', views.CashierLoginView.as_view()),

    path('finishcashier/', views.FinishCashierView.as_view()),
    path('sendcashierid/', views.CashierIDView.as_view()),

    path('checkusername/', views.CheckUsernameView.as_view()),
    path('checkphone/', views.CheckPhoneView.as_view()),
]
