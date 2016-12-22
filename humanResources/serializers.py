from django.contrib.auth.models import User
from rest_framework import serializers
from models import SetUpUser, HumanResourceProfile


class SetUpUserSerializer(serializers.ModelSerializer):

    company = serializers.CharField(required=False)
    magic_link = serializers.CharField(required=False)
    is_active = serializers.SerializerMethodField('has_relationship')


    def has_relationship(self, instance):
        return User.objects.filter(email=instance.email).exists()

    class Meta:
        model = SetUpUser
        fields = ('id', 'company', 'email', 'magic_link', 'is_active')


class HumanResourceProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = HumanResourceProfile
        fields = "__all__"

