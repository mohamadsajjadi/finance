from django.contrib import admin
from .models import CreditRequest, Transaction, Store

admin.site.register(Store)
admin.site.register(CreditRequest)
admin.site.register(Transaction)
