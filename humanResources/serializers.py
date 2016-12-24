from django.contrib.auth.models import User
from rest_framework import serializers
from models import SetUpUser, HumanResourceProfile


class SetUpUserSerializer(serializers.ModelSerializer):

    company = serializers.CharField(required=False)
    magic_link = serializers.CharField(required=False)

    class Meta:
        model = SetUpUser
        fields = ('id', 'company', 'email', 'magic_link', 'is_active')
        read_only_fields = ('id',)


class HumanResourceProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = HumanResourceProfile
        fields = "__all__"

