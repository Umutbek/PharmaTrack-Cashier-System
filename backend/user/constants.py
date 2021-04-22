from django.db import models


class UserTypes(models.IntegerChoices):
    CASHIER = 0, 'Кассир'
    MANAGER = 1, 'Менеджер'
