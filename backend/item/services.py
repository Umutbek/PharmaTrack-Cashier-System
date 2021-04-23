from datetime import datetime

from item.models import CashierWorkShift


# CashierWorkShift helper methods
def get_active_cashier_work_shift(cashier):
    return CashierWorkShift.objects.get(cashier=cashier, date_start__isnull=False, date_end__isnull=True)


def start_work_shift(cashier):
    cashier_history = CashierWorkShift.objects.create(
        date_start=datetime.now(),
        date_end=None,
        cashier=cashier,
        store=cashier.store,  # у кассира может меняться аптека
    )
    return cashier_history


def end_work_shift(cashier):
    try:
        cashier_history = get_active_cashier_work_shift(cashier)
        cashier_history.date_end = datetime.now()
        cashier_history.save()
        return cashier_history
    except CashierWorkShift.DoesNotExist as e:
        return None
