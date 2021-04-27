from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)

from item.utils import ClientTypes
from user.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=200, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    objects = UserManager()
    USERNAME_FIELD = 'username'

    @property
    def fullname(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def is_cashier(self):
        return hasattr(self, 'cashier')

    def is_manager(self):
        return hasattr(self, 'manager')

    def __str__(self):
        return self.fullname


class Cashier(User):
    store = models.ForeignKey('item.Store', on_delete=models.CASCADE, related_name='cashiers')


class Manager(User):
    pass


class Client(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    pension_book = models.CharField(max_length=200)

    type = models.IntegerField(choices=ClientTypes.choices, default=ClientTypes.REGULAR)

    def save(self, *args, **kwargs):
        if self.pension_book and len(self.pension_book) > 0:
            self.type = ClientTypes.PENSIONER
        return super(Client, self).save(*args, **kwargs)
