from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from models import *


class EmailSerializer(ModelSerializer):
    class Meta:
        model = Email


class ReferalSerializer(ModelSerializer):

    refree = serializers.SlugRelatedField(
        slug_field='email',
        queryset=Email.objects.all()
     )

    class Meta:
        model = Referal
