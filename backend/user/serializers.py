from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)
from rest_framework_simplejwt.state import token_backend
from user.models import Cashier, Manager
from item.services import (start_work_shift,
                           get_active_cashier_work_shift)
from item.models import CashierWorkShift
from user.constants import UserTypes


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
        }

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        return self.Meta.model.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        else:
            raise ValidationError({'password': 'Введите пароль'})
        return user


class CashierSerializer(UserSerializer):
    class Meta:
        model = Cashier
        fields = ('id', 'username', 'password', 'store',
                  'first_name', 'last_name', 'fullname')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class ManagerSerializer(UserSerializer):
    class Meta:
        model = Manager
        fields = ('id', 'username', 'password',
                  'first_name', 'last_name', 'fullname')
        extra_kwargs = {
            'password': {'write_only': True}
        }


def get_user_context(user):
    data = {}
    if user.is_cashier():
        user_data = CashierSerializer(user.cashier).data
        user_data['type'] = UserTypes.CASHIER
        try:
            active_work_shift = get_active_cashier_work_shift(user.cashier)
        except CashierWorkShift.DoesNotExist:
            active_work_shift = start_work_shift(user.cashier)
        user_data['date_start'] = active_work_shift.date_start
    elif user.is_manager():
        user_data = ManagerSerializer(user.manager).data
        user_data['type'] = UserTypes.MANAGER
    else:
        raise AuthenticationFailed()
    data['user'] = user_data

    return data


class TokenObtainPairWithUserInfoSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data = {**data, **get_user_context(self.user)}
        return data


class TokenRefreshWithUserInfoSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        decoded_payload = token_backend.decode(data['access'], verify=True)
        user = User.objects.get(id=decoded_payload['user_id'])
        data = {**data, **get_user_context(user)}
        return data
