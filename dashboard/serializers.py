from django.contrib.auth import get_user_model
from rest_framework import serializers
from dashboard.models import UserProfile, Module, QuovoUser
from data.models import Account


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('email',)


class UserWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = "__all__"


class UserProfileWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("birthday", "company")


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ("id", "brokerage_name", "nickname")


class UserProfileReadSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    accounts = serializers.SerializerMethodField('quovo_user_accounts', read_only=True)

    def quovo_user_accounts(self, parent):
        accounts = parent.quovoUser.userAccounts.filter(active=True)
        return AccountSerializer(accounts, many=True).data

    class Meta:
        model = UserProfile
        fields = "__all__"


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        exclude = ("id",)


class QuovoUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = QuovoUser
        fields = "__all__"
