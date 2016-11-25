from rest_framework import serializers
from models import SetUpUser


class SetUpUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = SetUpUser
        fields = ('id', 'company', 'email', 'magic_link')

