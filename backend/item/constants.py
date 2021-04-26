from django.db import models


class ClientOrderStatuses(models.IntegerChoices):
    NEW = 1, 'Новые'
    PACKING = 2, 'Упаковывается'
    ON_THE_WAY = 3, 'В пути'
    COMPLETED = 4, 'Завершенные'
    DECLINED = 5, 'Отказано'


class StoreOrderStatuses(models.IntegerChoices):
    NEW = 1, 'Новый'
    SENT = 2, 'Отгружено'
    DELIVERED = 3, 'Доставлено'
