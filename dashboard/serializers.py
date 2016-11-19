from rest_framework import serializers
from models import User, UserProfile, Module, QuovoUser


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')


class UserWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = "__all__"


class UserProfileWriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ("firstName", "lastName", "birthday", "state", "company", "zipCode")


class UserProfileReadSerializer(serializers.ModelSerializer):

    user = UserSerializer()

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

