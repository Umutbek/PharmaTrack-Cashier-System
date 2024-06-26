from django.urls import path, include
from user import views
from rest_framework.routers import DefaultRouter

app_name = 'user'

router = DefaultRouter()
router.register(r'cashiers', views.CashierViewSet)
router.register(r'managers', views.ManagerViewSet)
router.register(r'clients', views.ClientViewSet)

urlpatterns = [
    path('users/login/', views.Login.as_view()),
    path('users/logout/', views.Logout.as_view()),
    path('users/current/', views.CurrentUser.as_view()),
    path('', include(router.urls)),
]
