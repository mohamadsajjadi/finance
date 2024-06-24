# import decimal
#
# from django.utils import timezone
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.db import transaction
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework.views import APIView
#
# from account.models import User
# from .models import Store, CreditRequest, Transaction
# from .serializers import StoreSerializer, CreditRequestSerializer, TransactionSerializer
#
#
# class StoreViewSet(viewsets.ModelViewSet):
#     queryset = Store.objects.all()
#     serializer_class = StoreSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
#     def approve(self, request, pk=None):
#         store = self.get_object()
#         if store.approved:
#             return Response({'status': 'Already approved'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             with transaction.atomic():
#                 store.approved = True
#                 store.save()
#         except Exception as e:
#             return Response({'status': 'Error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response({'status': 'Store approved'})
#
#
# class CreditRequestViewSet(viewsets.ModelViewSet):
#     queryset = CreditRequest.objects.all()
#     serializer_class = CreditRequestSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.save(store=self.request.user.store)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
#     def approve(self, request, pk=None):
#         credit_request = self.get_object()
#
#         if not request.user.is_superuser:
#             return Response({'status': 'Permission Denied!'}, status=status.HTTP_403_FORBIDDEN)
#
#         if credit_request.approved:
#             return Response({'status': 'Already approved!'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             with transaction.atomic():
#                 credit_request.approved = True
#                 credit_request.approved_at = timezone.now()
#                 credit_request.save()
#
#         except Exception as e:
#             return Response({'status': 'Error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#
#         return Response({'status': 'Credit request approved'})
#
#
# class ChargeView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         store = request.user.store
#         phone_number = request.data.get('phone_number')
#         amount = request.data.get('amount')
#
#         if not store:
#             return Response({'status': 'Store not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         if not phone_number or not amount:
#             return Response({'status': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             customer = User.objects.get(phone_number=phone_number)
#         except User.DoesNotExist:
#             return Response({'status': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         if customer.role != 'customer':
#             return Response({'status': 'Invalid customer'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if store.credit_balance < decimal.Decimal(amount):
#             return Response({'status': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
#
#         if store.credit_balance < decimal.Decimal(amount):
#             return Response({'status': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             with transaction.atomic():
#                 transaction_obj = Transaction.objects.create(
#                     store=store,
#                     phone_number=phone_number,
#                     amount=amount
#                 )
#                 store.credit_balance -= decimal.Decimal(amount)
#                 store.save()
#
#                 customer.charge_amount += decimal.Decimal(amount)
#                 customer.save()
#
#                 serializer = TransactionSerializer(transaction_obj)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         except Exception as e:
#             return Response({'status': 'Error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from .models import Store, CreditRequest, Transaction
from .serializers import StoreSerializer, CreditRequestSerializer, TransactionSerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        store = self.get_object()
        if store.approved:
            return Response({'status': 'Already approved'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                store.approved = True
                store.save()
        except Exception as e:
            return Response({'status': 'Error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Store approved'})


class CreditRequestViewSet(viewsets.ModelViewSet):
    queryset = CreditRequest.objects.all()
    serializer_class = CreditRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        credit_request = self.get_object()

        if credit_request.approved:
            return Response({'status': 'Already approved!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                credit_request_serializer = self.get_serializer(credit_request)
                credit_request_serializer.approve()
        except Exception as e:
            return Response({'status': 'Error', 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'Credit request approved'})


class ChargeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            transaction_obj = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
