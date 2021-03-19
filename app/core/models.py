import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
                                       BaseUserManager, PermissionsMixin
from django.db.models import Q
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
import random
import os


class UserManager(BaseUserManager):
    """Manager for user profiles"""
    def create_user(self, login, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not login:
            raise ValueError('User must have an login')

        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password):
        """Create a superuser"""
        user = self.create_user(login, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Model for Regular account"""
    store = 1
    depot = 2

    choice = (
        (store, "store"),
        (depot, "depot"),
    )

    login = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=200, choices=choice, null=True)
    name = models.CharField(max_length=200, null=True)
    address = models.TextField()
    date = models.DateTimeField(auto_now_add=True, null=True)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'login'

    def __str__(self):
        return self.login


class Cashier(models.Model):
    """Model for Cashier"""
    admin = 1
    cashier = 2

    choice = (
        (admin, "admin"),
        (cashier, "cashier"),
    )
    fullname = models.CharField(max_length=200)
    phone = models.CharField(max_length=50)
    type = models.CharField(max_length=200, choices=choice, null=True)
    store = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    password = models.CharField(max_length=200)
    lastdate = models.CharField(max_length=200, null=True, blank=True)
    finishdayid = models.IntegerField(null=True, blank=True)


class CashierLogin(models.Model):
    """Serializer for Cashier"""
    phone = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    lastdate = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return self.phone


class Category(models.Model):
    """Model for category"""
    name = models.CharField(max_length=200)
    storeid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="store", null=True)
    totalCost = models.FloatField(default=0)
    totalQuantity = models.FloatField(default=0)


class GlobalItem(models.Model):
    """Model for itemGlobal"""
    uniqueid = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    producer = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class FarmStoreItems(models.Model):
    """Model for FarmStoreItems"""
    globalitem = models.ForeignKey(GlobalItem, on_delete=models.CASCADE, null=True, blank=True)
    seria = models.CharField(max_length=200, null=True)
    sepparts = models.FloatField(null=True)
    deadline = models.CharField(max_length=200, null=True, blank=True)
    cost = models.FloatField(null=True)
    totalcost = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.globalitem.name


class Item(models.Model):
    """Model for Active Items"""
    farmstoreitems = models.ForeignKey(FarmStoreItems, on_delete=models.CASCADE, null=True)
    quantity = models.FloatField(null=True, blank=True)
    costsale= models.FloatField(null=True, blank=True)
    issale = models.BooleanField(default=False, null=True)
    parts = models.FloatField(null=True, blank=True)
    totalcost = models.FloatField(null=True, blank=True)
    storeid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activestore", null=True)


class AddStoreItem(models.Model):
    """Model for new item add to store"""
    uniqueid = models.CharField(max_length=200, null=True)
    seria = models.CharField(max_length=200, null=True)
    sepparts = models.FloatField(null=True)
    quantity = models.IntegerField(null=True)
    storeid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="itemadd", null=True)


class ItemsIn(models.Model):
    """Model for store order"""
    uniqueid = models.IntegerField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    datesent = models.DateTimeField(auto_now_add=True, null=True)
    datereceived = models.DateTimeField(auto_now_add=True, null=True)
    depotid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="depotid", null=True)

    storedepotid = models.ForeignKey(User, on_delete=models.CASCADE, related_name="storedepotid", null=True)
    totalCount = models.IntegerField(default=0)
    totalCost = models.FloatField(default=0)
    status = models.BooleanField(default=False)
    iseditable = models.BooleanField(default=True)

    def storeorderitem(self):
        return self.storeorder_set.all()


class StoreOrder(models.Model):
    """Model for store order"""
    itemin = models.ForeignKey(ItemsIn, on_delete=models.CASCADE, null=True)
    farmstoreitems = models.ForeignKey(FarmStoreItems, on_delete=models.CASCADE, related_name="storeorder", null=True)
    quantity = models.IntegerField(null=True, blank=True)
    costTotal = models.FloatField(default=0)


class OrderReceived(models.Model):
    """Model for order receive"""
    orderid = models.ForeignKey(ItemsIn, on_delete=models.CASCADE, null=True)


class CheckUsername(models.Model):
    """Model for checkusername"""
    username = models.CharField(max_length=200)

    def __str__(self):
        return self.username


class ClientOrder(models.Model):
    """Model for client order"""
    datetime = models.DateTimeField(auto_now_add=True, null=True)
    cashier = models.ForeignKey(Cashier, on_delete=models.CASCADE, null=True, blank=True)
    countitem = models.IntegerField(null=True)
    total = models.FloatField(default=0)
    status = models.BooleanField(default=False)

    @property
    def clientorder(self):
        return self.clientorderitem_set.all()


class ClientOrderItem(models.Model):
    """Model for Transaction Item"""
    transactionid = models.ForeignKey(ClientOrder, on_delete=models.CASCADE, null=True, blank=True)
    farmstoreitems = models.ForeignKey(FarmStoreItems, on_delete=models.CASCADE, related_name="transaction", null=True)
    quantity = models.FloatField(null=True, blank=True)
    sepparts = models.FloatField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)
    costone = models.FloatField()
    costtotal = models.FloatField(default=0)


class OrderReceivedClient(models.Model):
    """Model for order receive"""
    clientorderid = models.ForeignKey(ClientOrder, on_delete=models.CASCADE, null=True)


class FinishCashier(models.Model):
    """Serializer for finish cashier"""
    transactions = models.ManyToManyField('ClientOrder')
    datestart = models.DateTimeField(null=True, blank=True)
    dateend = models.DateTimeField(null=True, blank=True)
    cashier = models.ForeignKey(Cashier, on_delete=models.CASCADE, null=True, blank=True)
    total = models.FloatField(null=True, blank=True)
    tottrans = models.FloatField(null=True, blank=True)


class CashierID(models.Model):
    """Model for CashierID"""
    cashierid = models.ForeignKey(Cashier, on_delete=models.CASCADE, null=True, blank=True)
    finishdayid = models.IntegerField(null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True,null=True)


class Report(models.Model):
    """Model for Report"""
    datefrom = models.DateField(null=True, blank=True)
    dateto = models.DateField(null=True, blank=True)
    inTotal = models.IntegerField(default=0)
    incomeTotal = models.IntegerField(default=0)
    earnTotal = models.IntegerField(default=0)