from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from user.models import Cashier
from item.constants import StoreOrderStatuses


User = get_user_model()


class StoreAbstract(models.Model):
    name = models.CharField(max_length=200, null=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    phone = models.CharField(max_length=200)
    email = models.EmailField(max_length=200, null=True, blank=True)

    class Meta:
        abstract = True


class Store(StoreAbstract):
    pass


class Depot(StoreAbstract):
    pass


class Category(models.Model):
    """ Категория товара """
    name = models.CharField(max_length=200)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="categories", null=True)
    total_cost = models.FloatField(default=0)
    total_quantity = models.FloatField(default=0)

    class Meta:
        ordering = ['total_quantity']


class GlobalItem(models.Model):
    """ Здесь хранятся все возможные товары """
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    unique_id = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    producer = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='global-items/', default='global-items/default.png')
    series = models.CharField(max_length=200, null=True)
    sepparts = models.FloatField(null=True)
    expiration_date = models.DateTimeField()
    price_selling = models.FloatField(null=True)

    class Meta:
        ordering = ['name']


class StoreItem(models.Model):
    """ Здесь хранятся товары относящиеся только одной аптеке"""
    global_item = models.ForeignKey(GlobalItem, on_delete=models.CASCADE, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="items", null=True, db_index=True)
    quantity = models.FloatField(default=1, validators=[MinValueValidator(1)])
    is_sale = models.BooleanField(default=False)
    parts = models.FloatField(null=True, blank=True)
    total_cost = models.FloatField(null=True, blank=True)
    price_sale = models.FloatField(validators=[MinValueValidator(0)])
    price_received = models.FloatField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['store', ], name='store_index')
        ]


class StoreOrder(models.Model):
    """ Чтобы сделать заказ на склад, используйте эту модель"""
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, related_name="depot")
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name="store")
    unique_id = models.CharField(max_length=255, null=False, unique=True)
    address = models.TextField(null=True, blank=True)
    date_sent = models.DateTimeField(auto_now_add=True)
    date_received = models.DateTimeField(null=True)
    status = models.IntegerField(choices=StoreOrderStatuses.choices, default=StoreOrderStatuses.NEW)
    is_editable = models.BooleanField(default=True)
    total_cost = models.IntegerField(default=0)
    total_cnt = models.IntegerField(default=0)
    # todo: set statuses


class StoreOrderItem(models.Model):
    """ Товары и их количество для заказа на склад"""
    store_order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE, related_name="store_ordered_items", null=True)
    global_item = models.ForeignKey(GlobalItem, on_delete=models.CASCADE, related_name="store_ordered_items", null=True)
    quantity = models.IntegerField(null=True, blank=True)

    @property
    def cost_total(self):
        return self.global_item.cost * self.quantity


class ClientOrder(models.Model):
    """ Здесь хранятся заказы клиентов """
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_orders')
    date_ordered = models.DateTimeField(auto_now_add=True, null=True)
    count_item = models.IntegerField(null=True)
    total_sum = models.FloatField(default=0)
    status = models.BooleanField(default=False)
    # todo: set statuses


class ClientOrderedItem(models.Model):
    """ Товары по каждому заказу клиентов """
    client_order = models.ForeignKey(ClientOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='client_ordered_items')
    global_item = models.ForeignKey(GlobalItem, on_delete=models.SET_NULL, null=True, blank=True, related_name="client_ordered_items")
    quantity = models.FloatField(null=True)
    sepparts = models.FloatField(null=True)
    date_ordered = models.DateTimeField(auto_now_add=True, null=True)
    cost_one = models.FloatField()
    cost_total = models.FloatField(default=0)


class CashierWorkShift(models.Model):
    """
    Здесь мы храним информацию о смене персонала: кто в какое время работал,
    сколько и на какую сумму продаж сделал
    """
    client_orders = models.ManyToManyField('ClientOrder')
    cashier = models.ForeignKey(Cashier, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    date_start = models.DateTimeField()
    date_end = models.DateTimeField(null=True)
    # todo: cashier can have only one date_end=null


class Report(models.Model):
    """ Отчеты по периодам """
    date_from = models.DateField()
    date_to = models.DateField()
    in_total = models.IntegerField(default=0)
    income_total = models.IntegerField(default=0)
    earn_total = models.IntegerField(default=0)

