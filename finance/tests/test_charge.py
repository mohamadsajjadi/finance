# import pytest
# from decimal import Decimal
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token
# from account.models import User
# from finance.models import Store
# from concurrent.futures import ThreadPoolExecutor
#
#
# @pytest.mark.django_db(transaction=True)
# def test_charge_parallel():
#     owner = User.objects.create_user(username='store_owner', password='ownerpass')
#     store = Store.objects.create(owner=owner, name='Test Store', credit_balance=1000)
#
#     customer = User.objects.create_user(username='customer', password='custpass', phone_number='12345678901',
#                                         role='customer')
#
#     client = APIClient()
#     token = Token.objects.create(user=owner)
#     client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
#
#     def charge_customer():
#         response = client.post(reverse('charge'), {'phone_number': '12345678901', 'amount': 500})
#         return response.status_code
#
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         results = list(executor.map(lambda _: charge_customer(), range(2)))
#
#     store.refresh_from_db()
#     customer.refresh_from_db()
#
#     assert results.count(201) == 1
#     assert results.count(400) == 1
#     assert store.credit_balance == Decimal('500.000')
#     assert customer.charge_amount == Decimal('500.000')

#
# import pytest
# from decimal import Decimal
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token
# from account.models import User
# from finance.models import Store, Transaction
# from concurrent.futures import ThreadPoolExecutor
#
#
# @pytest.mark.django_db(transaction=True)
# def test_charge_parallel_large_scale():
#     owner = User.objects.create_user(username='store_owner', password='ownerpass')
#     store = Store.objects.create(owner=owner, name='Test Store', credit_balance=10000)
#
#     customer = User.objects.create_user(username='customer', password='custpass', phone_number='12345678901',
#                                         role='customer')
#
#     client = APIClient()
#     token = Token.objects.create(user=owner)
#     client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
#
#     def charge_customer():
#         response = client.post(reverse('charge'), {'phone_number': '12345678901', 'amount': 100})
#         return response.status_code
#
#     num_requests = 5
#
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         results = list(executor.map(lambda _: charge_customer(), range(num_requests)))
#
#     store.refresh_from_db()
#     customer.refresh_from_db()
#
#     assert results.count(201) == num_requests
#     assert store.credit_balance == Decimal('10000.000') - Decimal('100') * num_requests
#     assert customer.charge_amount == Decimal('100') * num_requests


import pytest
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from account.models import User
from finance.models import Store, Transaction
from concurrent.futures import ThreadPoolExecutor
from django.db import transaction


@pytest.mark.django_db(transaction=True)
def test_charge_parallel_large_scale():
    owner = User.objects.create_user(username='store_owner', password='ownerpass')
    store = Store.objects.create(owner=owner, name='Test Store', credit_balance=10000)

    customer = User.objects.create_user(username='customer', password='custpass', phone_number='12345678901',
                                        role='customer')

    client = APIClient()
    token = Token.objects.create(user=owner)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def charge_customer():
        with transaction.atomic():
            response = client.post(reverse('charge'), {'phone_number': '12345678901', 'amount': 100})
            return response.status_code

    num_requests = 50

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: charge_customer(), range(num_requests)))

    store.refresh_from_db()
    customer.refresh_from_db()

    assert results.count(201) == num_requests
    assert store.credit_balance == Decimal('10000.000') - Decimal('100') * num_requests
    assert customer.charge_amount == Decimal('100') * num_requests
