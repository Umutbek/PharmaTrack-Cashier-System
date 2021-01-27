from django.urls import path, include
from item import views

app_name = 'item'

urlpatterns = [
    path('category/', views.CategoryView.as_view()),
    path('getcategory/', views.GetCategoryView.as_view()),

    path('globalitem/', views.GlobalItemView.as_view()),
    path('items/', views.ActiveItemsView.as_view()),
    path('sendorderid/', views.OrderIdView.as_view()),

    path('itemsin/', views.ItemsInView.as_view()),

    path('clientorder/', views.ClientOrderView.as_view()),
    path('clientitemorder/', views.ClientItemOrderView.as_view()),
    path('clientorder/<int:pk>', views.ClientOrderDetailView.as_view()),

    path('getreport/', views.ReportView.as_view())
]
