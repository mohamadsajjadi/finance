# from rest_framework import serializers
# from .models import Store, CreditRequest, Transaction
#
#
# class StoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Store
#         fields = ['id', 'owner', 'name', 'approved', 'created_at', 'credit_balance']
#         read_only_fields = ['owner', 'approved', 'created_at', 'credit_balance']
#
#
# class CreditRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CreditRequest
#         fields = ['id', 'store', 'amount', 'approved', 'created_at', 'approved_at']
#         read_only_fields = ['store', 'approved', 'created_at', 'approved_at']
#
#
# class TransactionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Transaction
#         fields = ['id', 'store', 'phone_number', 'amount', 'created_at']
#         read_only_fields = ['store', 'created_at']
import decimal

from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from .models import Store, CreditRequest, Transaction
from account.models import User


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'owner', 'name', 'approved', 'created_at', 'credit_balance']
        read_only_fields = ['owner', 'approved', 'created_at', 'credit_balance']

    def validate(self, attrs):
        # اضافه کردن ولیدیشن‌های لازم برای Store
        return attrs


class CreditRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditRequest
        fields = ['id', 'store', 'amount', 'approved', 'created_at', 'approved_at']
        read_only_fields = ['store', 'approved', 'created_at', 'approved_at']

    def validate(self, attrs):
        # اضافه کردن ولیدیشن‌های لازم برای CreditRequest
        return attrs

    def approve(self):
        self.instance.approved = True
        self.instance.approved_at = timezone.now()
        self.instance.save()


class TransactionSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'store', 'phone_number', 'amount', 'created_at']
        read_only_fields = ['store', 'created_at']

    def validate_phone_number(self, value):
        try:
            customer = User.objects.get(phone_number=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Customer not found")

        if customer.role != 'customer':
            raise serializers.ValidationError("Invalid customer")

        return value

    def validate(self, attrs):
        store = self.context['request'].user.store
        amount = decimal.Decimal(attrs['amount'])

        if store.credit_balance < amount:
            raise serializers.ValidationError("Insufficient balance")

        return attrs

    def create(self, validated_data):
        store = self.context['request'].user.store
        phone_number = validated_data.pop('phone_number')
        amount = decimal.Decimal(validated_data['amount'])
        customer = User.objects.get(phone_number=phone_number)

        try:
            # with transaction.atomic():
            # store = Store.objects.select_for_update().get(pk=store.pk)
            # customer = User.objects.select_for_update().get(pk=customer.pk)
            #     transaction_obj = Transaction.objects.create(
            #         store=store,
            #         phone_number=phone_number,
            #         amount=amount
            #     )

            with transaction.atomic():
                transaction_obj = Transaction.objects.create(
                    store=store,
                    phone_number=phone_number,
                    amount=amount
                )

            store.credit_balance -= amount
            store.save()

            customer.charge_amount += amount
            customer.save()

        except Exception as e:
            raise serializers.ValidationError(f"Error occurred: {str(e)}")

        return transaction_obj
