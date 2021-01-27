from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate, password_validation
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

from core import models

from rest_framework.authtoken.models import Token

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id','login', 'name', 'type', 'address', 'phone',
                  'email', 'date', 'password'
                 )
        extra_kwargs = {'password':{'write_only':True},}

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(
        style = {'input_type':'password'}, trim_whitespace=False
    )

    def validate(self, data):

        login = data.get('login')
        password = data.get('password')

        if login is None:
            raise serializers.ValidationError(
                'A login is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(
            request = self.context.get('request'),
            login=login,
            password=password,
        )

        if not user:
            msg = _('Wrong phone or password')
            raise serializers.ValidationError(msg, code='authorization')

        data['user']=user
        return data


class CheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CheckUsername
        fields = ("id", "username")
        read_only_fields = ('id',)


class CashierLoginSerializer(serializers.ModelSerializer):
    """Serializer for cashier login"""

    class Meta:
        model = models.CashierLogin
        fields = (
            'id', 'phone', 'password'
        )
        read_only_fields=('id',)


class CashierSerializer(serializers.ModelSerializer):
    """Serializer for Cashier"""

    class Meta:
        model = models.Cashier
        fields = (
            'id', 'fullname', 'phone', 'type',
            'store', 'lastdate', 'password', 'finishdayid'
        )
        read_only_fields = ('lastdate', 'finishdayid')
        extra_kwargs = {'password':{'write_only':True},}

    def create(self, validated_data):
        """Create user with encrypted password and return it"""
        return models.Cashier.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """Update a cashier, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()
        return user


class CashierLoginSerializer(serializers.ModelSerializer):
    """Serializer for cashier login"""

    class Meta:
        model = models.CashierLogin
        fields = (
            'id', 'phone', 'password'
        )
        read_only_fields=('id',)


class FinishCashierSerializer(serializers.ModelSerializer):
    """Serializer for finishcashier"""

    class Meta:
        model = models.FinishCashier
        fields = (
            'id', 'transactions', 'datestart', 'dateend', 'cashier', 'total', 'tottrans'
        )
        read_only_fields=('id',)


class CashierIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CashierID
        fields = ("id", "cashierid", 'finishdayid', 'datetime')
        read_only_fields = ('id',)
