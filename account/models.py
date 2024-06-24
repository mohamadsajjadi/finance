from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    Roles = (
        ('admin', 'Admin'),
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )
    role = models.CharField(max_length=10, choices=Roles, default='Customer')
    phone_number = models.CharField(max_length=11, unique=True, db_index=True)
    charge_amount = models.DecimalField(max_digits=10, decimal_places=3, default=0.000)

    def __str__(self):
        return f'{self.username} - {self.role}'
