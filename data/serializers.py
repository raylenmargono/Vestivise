from rest_framework import serializers
from models import *


class HoldingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Holding
        fields = "__all__"


class UserCurrentHolding(serializers.ModelSerializer):

    class Meta:
        model = UserCurrentHolding
        fields = "__all__"


class UserDisplayHoldingSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDisplayHolding
        fields = "__all__"


class HoldingPriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = HoldingPrice
        fields = "__all__"


class HoldingExpenseRatioSerializer(serializers.ModelSerializer):

    class Meta:
        model = HoldingExpenseRatio
        fields = "__all__"


class HoldingAssetBreakdownSerializer(serializers.ModelSerializer):

    class Meta:
        model = HoldingAssetBreakdown
        fields = "__all__"
