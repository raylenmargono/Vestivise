from rest_framework import serializers
from models import SetUpUser


class SetUpUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = SetUpUser
        fields = "__all__"

