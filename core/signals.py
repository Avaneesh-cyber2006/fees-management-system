from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import FeeDetails, FeeInstallments


@receiver(post_save, sender=FeeInstallments)
@receiver(post_delete, sender=FeeInstallments)
def sync_fee_details_on_installment_change(sender, instance, **kwargs):
    """Keep FeeDetails.fees_remaining in sync when installments change."""
    try:
        instance.registration_no.feedetails.sync_from_installments()
    except FeeDetails.DoesNotExist:
        pass
