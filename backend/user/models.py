from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)
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

    def __str__(self):
        return self.fullname


class Cashier(User):
    store = models.ForeignKey('item.Store', on_delete=models.CASCADE, related_name='cashiers')


class Manager(User):
    pass
