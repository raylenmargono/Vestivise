from rest_framework import serializers
from account.models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')


class UserWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class UserProfileWriteSerializer(serializers.ModelSerializer):

    user = UserWriteSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"

    def create(self, validated_data):
        user = None
        userData = validated_data.pop('user')
        user = User.objects.create_user(**userData)
        profile = UserProfile.objects.create(user=user.id, **validated_data)
        return profile


class UserProfileReadSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = "__all__"


class AccountModuleSerializer(serializers.ModelSerializer):

    module = ModuleSerializer(read_only=True)

    class Meta:
        model = AccountModule
        fields = "__all__"


class BasicAccountSerializer(serializers.ModelSerializer):

    account_modules = AccountModuleSerializer(many=True, read_only=True)

    class Meta:
        model = BasicAccount
        fields = "__all__"
