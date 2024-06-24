import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from account.models import User
from finance.models import Store, CreditRequest
from concurrent.futures import ThreadPoolExecutor
from django.utils import timezone


@pytest.mark.django_db(transaction=True)
def test_credit_request_approval_parallel_large_scale():
    user = User.objects.create_user(username='admin', password='admin', is_superuser=True)
    store = Store.objects.create(owner=user, name='Test Store', credit_balance=0)


    num_requests = 500
    credit_requests = [CreditRequest.objects.create(store=store, amount=100) for _ in range(num_requests)]

    client = APIClient()
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def approve_credit_request(credit_request):
        credit_request.approved = True
        credit_request.approved_at = timezone.now()
        credit_request.save()
        return 200

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(approve_credit_request, credit_requests))


    assert results.count(200) == num_requests


    store.refresh_from_db()
    assert store.credit_balance == 100 * num_requests
