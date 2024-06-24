from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        return value

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserSerializer, self).create(validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, data):
        username = data.get('username')
        phone_number = data.get('phone_number')
        password = data.get('password')

        if not username or not phone_number or not password:
            raise serializers.ValidationError('Please provide both username, phone number, and password.')

        user = authenticate(username=username, password=password)

        if user is None or user.phone_number != phone_number:
            raise serializers.ValidationError('Invalid credentials')

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return {'token': token.key}
