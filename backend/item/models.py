from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django_fsm import FSMIntegerField, transition

from item.constants import StoreOrderStatuses
from user.models import Cashier

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


class GlobalItem(models.Model):
    """ Здесь хранятся все возможные товары """
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    unique_id = models.CharField(max_length=200, null=False, unique=True)
    name = models.CharField(max_length=200)
    producer = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='global-items/', default='global-items/default.png')
    series = models.CharField(max_length=200, null=True)
    expiration_date = models.DateTimeField()
    price_selling = models.FloatField(null=True)
    max_num_pieces = models.IntegerField(default=1, null=False)

    class Meta:
        ordering = ['name']


class StoreItem(models.Model):
    """ Здесь хранятся товары относящиеся только одной аптеке"""
    global_item = models.ForeignKey(GlobalItem, on_delete=models.CASCADE, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="items", null=True, db_index=True)
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    num_pieces = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_sale = models.BooleanField(default=False)

    @property
    def total_num_pieces(self):
        return self.quantity * self.global_item.max_num_pieces + self.num_pieces

    class Meta:
        indexes = [
            models.Index(fields=['store', ], name='store_index')
        ]
        constraints = [
            models.UniqueConstraint(fields=['store', 'global_item'], name='unique_store_global_item')
        ]


class StoreOrderHistory(models.Model):
    store_order = models.ForeignKey('StoreOrder', on_delete=models.SET_NULL, null=True, related_name='history')
    store_order_data = models.JSONField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # todo: make read only after save

    class Meta:
        ordering = ('store_order', 'created_at')


class StoreOrder(models.Model):
    """ Чтобы сделать заказ на склад, используйте эту модель"""
    depot = models.ForeignKey(Depot, on_delete=models.SET_NULL, null=True, related_name="depot")
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True, related_name="store")
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True)
    status = FSMIntegerField(choices=StoreOrderStatuses.choices, default=StoreOrderStatuses.NEW)

    @transition(field=status, source=[StoreOrderStatuses.NEW, StoreOrderStatuses.SENT], target=StoreOrderStatuses.NEW)
    def update_new(self):
        pass

    @transition(field=status, source=[StoreOrderStatuses.NEW, StoreOrderStatuses.SENT], target=StoreOrderStatuses.SENT)
    def send(self):
        pass

    @transition(field=status, source=[StoreOrderStatuses.SENT], target=StoreOrderStatuses.DELIVERED)
    def deliver(self):
        self.date_received = datetime.now()
        self.save_delivered_items()

    @property
    def ordered_items_sum(self):
        return sum([item.cost_total for item in self.store_ordered_items.all()])

    @property
    def ordered_items_cnt(self):
        return self.store_ordered_items.count()

    @property
    def total(self):
        return self.ordered_items_sum
        # todo: добавить скидку для пенсионеров

    @transaction.atomic
    def save_delivered_items(self):
        # сохранить все доставленные товары
        for item in self.store_ordered_items.all():
            store_item = StoreItem.objects.get(store=self.store,
                                               global_item=item.global_item)
            total_num_pieces = store_item.total_num_pieces + item.total_num_pieces
            store_item.quantity = total_num_pieces // store_item.global_item.max_num_pieces
            store_item.num_pieces = total_num_pieces % store_item.global_item.max_num_pieces
            store_item.save()


class StoreOrderItem(models.Model):
    """ Товары и их количество для заказа на склад"""
    store_order = models.ForeignKey(StoreOrder, on_delete=models.CASCADE, related_name="store_ordered_items", null=True)
    global_item = models.ForeignKey(GlobalItem, on_delete=models.CASCADE, related_name="store_ordered_items", null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    num_pieces = models.IntegerField(validators=[MinValueValidator(0)])

    @property
    def total_num_pieces(self):
        return self.quantity * self.global_item.max_num_pieces + self.num_pieces

    @property
    def cost_one(self):
        return self.global_item.price_selling

    @property
    def cost_total(self):
        return self.cost_one * (self.total_num_pieces / self.global_item.max_num_pieces)


class ClientOrder(models.Model):
    """ Здесь хранятся заказы клиентов """
    cashier = models.ForeignKey(Cashier, on_delete=models.CASCADE, related_name='client_orders')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='client_orders')
    date_ordered = models.DateTimeField(auto_now_add=True, null=True)
    status = models.IntegerField(choices=StoreOrderStatuses.choices, default=StoreOrderStatuses.NEW)

    @property
    def items_sum(self):
        return sum([item.cost_total for item in self.client_ordered_items.all()])

    def items_cnt(self):
        return self.client_ordered_items.count()


class ClientOrderedItem(models.Model):
    """ Товары по каждому заказу клиентов """
    client_order = models.ForeignKey(ClientOrder,
                                     on_delete=models.SET_NULL,
                                     null=True,
                                     blank=True,
                                     related_name='client_ordered_items')
    global_item = models.ForeignKey(GlobalItem,
                                    on_delete=models.SET_NULL,
                                    null=True,
                                    blank=True,
                                    related_name="client_ordered_items")
    quantity = models.FloatField(null=True)
    sepparts = models.FloatField(null=True)
    date_ordered = models.DateTimeField(auto_now_add=True, null=True)

    @property
    def cost_one(self):
        return self.global_item.price_selling

    @property
    def cost_total(self):
        return self.cost_one * self.quantity


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
