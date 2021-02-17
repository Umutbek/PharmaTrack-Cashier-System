from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from django.utils.translation import gettext as _

from core import models

class UserAdmin(BaseUserAdmin):

    list_display = ('phone', 'login')
    ordering = ('login',)
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        (_('Personal info'), {'fields': ('name', 'phone', 'type')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),

        (_('Important dates'), {'fields': ('last_login', )})

    )
    add_fieldsets = (
        (None, {
            'classes': ('wide', ),
            'fields': ('username', 'password1', 'password2')
        }),
    )

admin.site.register(models.User, UserAdmin)
admin.site.register(models.Cashier)
admin.site.register(models.GlobalItem)
admin.site.register(models.Item)
admin.site.register(models.Category)
admin.site.register(models.AddStoreItem)
admin.site.register(models.ItemsIn)
admin.site.register(models.StoreOrder)
admin.site.register(models.ClientOrder)
admin.site.register(models.ClientOrderItem)
