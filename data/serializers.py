from rest_framework import serializers
from data.models import *

class MoneySerializer(serializers.ModelSerializer):

	class Meta:
		model = Money 
		fields = '__all__'

class RefreshInfoSerializer(serializers.ModelSerializer):

	class Meta:
		model = RefreshInfo 
		fields = '__all__'

class RewardBalanceSerializer(serializers.ModelSerializer):

	class Meta:
		model = RewardBalance 
		fields = '__all__'

class YodleeAccountSerializer(serializers.ModelSerializer):
	_401kLoan = MoneySerializer(required=False)
	accountAmountDue = MoneySerializer(required=False)
	annuityBalance = MoneySerializer(required=False)
	availableBalance = MoneySerializer(required=False)
	availableCash = MoneySerializer(required=False)
	availableCredit = MoneySerializer(required=False)
	availableLoan = MoneySerializer(required=False)
	accountBalance = MoneySerializer(required=False)
	cash = MoneySerializer(required=False)
	cashValue = MoneySerializer(required=False)
	currentBalance = MoneySerializer(required=False)
	class Meta:
		model = YodleeAccount
		fields = '__all__'

class UserDataSerializer(serializers.ModelSerializer):
	yodleeaccount = YodleeAccountSerializer()
	class Meta:
		model = UserData 
		fields = '__all__'

class HoldingSerializer(serializers.ModelSerializer):

	class Meta:
		model = Holding 
		fields = '__all__'

class AssetClassificationSerializer(serializers.ModelSerializer):

	class Meta:
		model = AssetClassification 
		fields = '__all__'

class HistoricalBalanceSerializer(serializers.ModelSerializer):

	class Meta:
		model = HistoricalBalance 
		fields = '__all__'

class InvestmentPlanSerializer(serializers.ModelSerializer):

	class Meta:
		model = InvestmentPlan 
		fields = '__all__'

class InvestmentOptionSerializer(serializers.ModelSerializer):

	class Meta:
		model = InvestmentOption 
		fields = '__all__'

