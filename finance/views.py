from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from config.tasks import create_object

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

    # def perform_create(self, serializer):
    #     create_object.delay(serializer, self.request.user.store)

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
