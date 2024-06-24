import uuid

from django.db import models
from django.utils import timezone
from django.db import transaction

from account.models import User


class Store(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='store')
    name = models.CharField(max_length=50)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    credit_balance = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)

    def __str__(self):
        return f'{self.name}, owner: {self.owner}'


class CreditRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    store = models.ForeignKey(Store, on_delete=models.DO_NOTHING, related_name='credit_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Credit Request #{self.pk} - Store: {self.store.name}, Amount: {self.amount}'


class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='transaction')
    phone_number = models.CharField(max_length=11)
    amount = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.store.name} charged - {self.amount} to {self.phone_number}'
