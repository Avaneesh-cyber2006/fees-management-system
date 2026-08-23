"""Utilities for fee and installment calculations."""

from decimal import Decimal, ROUND_DOWN, InvalidOperation


def to_decimal(value, default=Decimal('0')):
    """Safely convert a value to Decimal for monetary calculations."""
    if value is None or value == '':
        return default
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return default


def split_amount_evenly(total, count):
    """
    Split total fees into equal installments with remainder on the last one.

    Example: 25000 / 3 -> [8333.33, 8333.33, 8333.34]
    """
    total = to_decimal(total)
    count = int(count)
    if count <= 0:
        return []
    if count == 1:
        return [total.quantize(Decimal('0.01'))]

    base = (total / count).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    amounts = [base] * count
    amounts[-1] = total - sum(amounts[:-1])
    return amounts


def get_installment_summary(installments):
    """Build installment summary stats from a queryset or list."""
    from django.db.models import Sum

    if hasattr(installments, 'aggregate'):
        total_amount = installments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
        total_count = installments.count()
        paid_count = installments.filter(status='Paid').count()
        pending_count = installments.exclude(status='Paid').count()
    else:
        installment_list = list(installments)
        total_amount = sum((to_decimal(i.amount) for i in installment_list), Decimal('0'))
        total_count = len(installment_list)
        paid_count = sum(1 for i in installment_list if i.status == 'Paid')
        pending_count = total_count - paid_count

    return {
        'total_count': total_count,
        'paid_count': paid_count,
        'pending_count': pending_count,
        'total_amount': total_amount,
    }
