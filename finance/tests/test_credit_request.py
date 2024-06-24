# import pytest
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token
# from account.models import User
# from finance.models import Store, CreditRequest
# from concurrent.futures import ThreadPoolExecutor
#
#
# @pytest.mark.django_db(transaction=True)
# def test_credit_request_approval_parallel():
#     user = User.objects.create_user(username='admin', password='admin', is_superuser=True)
#     store = Store.objects.create(owner=user, name='Test Store')
#     credit_request = CreditRequest.objects.create(store=store, amount=100, approved=True)
#     # credit_request.approved = True
#
#     client = APIClient()
#     token = Token.objects.create(user=user)
#     client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
#
#     def approve_request():
#         response = client.post(reverse('creditrequest-approve', args=[credit_request.id]))
#         return response.status_code
#
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         results = list(executor.map(lambda _: approve_request(), range(2)))
#
#     assert results.count(200) == 1
#     assert results.count(400) == 1
#
#     # Check the final state of the store's credit balance
#     store.refresh_from_db()
#     if credit_request.approved:
#         assert store.credit_balance == 100
#     else:
#         assert store.credit_balance == 0


# import pytest
# from django.urls import reverse
# from rest_framework.test import APIClient
# from rest_framework.authtoken.models import Token
# from account.models import User
# from finance.models import Store, CreditRequest
# from concurrent.futures import ThreadPoolExecutor
#
#
# @pytest.mark.django_db(transaction=True)
# def test_credit_request_approval_parallel():
#     user = User.objects.create_user(username='admin', password='admin', is_superuser=True)
#     store = Store.objects.create(owner=user, name='Test Store')
#     credit_request1 = CreditRequest.objects.create(store=store, amount=100)
#     credit_request2 = CreditRequest.objects.create(store=store, amount=100)
#
#     client = APIClient()
#     token = Token.objects.create(user=user)
#     client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
#
#     def create_credit_request(credit_request):
#         # شبیه‌سازی تغییر دستی تایید در پنل ادمین
#         credit_request.approved = True
#         credit_request.save()
#         return 200
#
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         results = list(executor.map(create_credit_request, [credit_request1, credit_request2]))
#
#     assert results.count(200) == 2
#
#     # بررسی وضعیت نهایی اعتبار فروشگاه
#     store.refresh_from_db()
#     assert store.credit_balance == 200


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

    # ایجاد تعداد زیادی درخواست اعتبار
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

    # بررسی نتایج درخواست‌ها
    assert results.count(200) == num_requests

    # بررسی وضعیت نهایی اعتبار فروشگاه
    store.refresh_from_db()
    assert store.credit_balance == 100 * num_requests
