from django.contrib import admin
from item import models


admin.site.register(models.Category)
admin.site.register(models.GlobalItem)
admin.site.register(models.StoreItem)
admin.site.register(models.StoreOrder)
admin.site.register(models.StoreOrderItem)
admin.site.register(models.ClientOrder)
admin.site.register(models.ClientOrderedItem)
admin.site.register(models.CashierWorkShift)
admin.site.register(models.Report)
