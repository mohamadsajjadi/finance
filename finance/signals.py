from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Store, CreditRequest


@receiver(post_save, sender=Store)
def update_user_role(sender, instance, created, **kwargs):
    if not created and instance.approved:
        instance.owner.role = 'vendor'
        instance.owner.save()


@receiver(post_save, sender=CreditRequest)
def update_store_credit_balance(sender, instance, created, **kwargs):
    if instance.approved:
        store = instance.store
        store.credit_balance += instance.amount
        store.save()
