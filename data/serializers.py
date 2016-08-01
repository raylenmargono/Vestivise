from rest_framework import serializers
from data.models import *
import data

YodleeAccountNestedModels = ['account401kLoan', 'accountAmountDue', 'annuityBalance',
'availableBalance', 'availableCash', 'availableCredit', 'availableLoan',
'accountBalance', 'cash', 'cashValue', 'currentBalance', 'faceAmount',
'lastPayment', 'accountLastPaymentAmount', 'marginBalance', 'maturiyAmount',
'minimumAmountDue', 'moneyMarketBalance', 'accountRefreshInfo', 
'runningBalance', 'totalCashLimit', 'totalCreditLine', 'totalUnvestedBalance',
'totalVestedBalance', 'escrowBalance', 'originalLoanAmount', 'principalBalance',
'recurringPayment', 'totalCreditLimit', 'rewardBalance', 'shortBalance',
'lastEmployeeContributionAmount']

YodleeAccountFeatures = ['accountID', 'accountName', 'accountNumber',
'apr', 'isAsset', 'classification', 'container', 'dueDate', 
'expirationDate', 'interestRate', 'lastPaymentDate', 'lastUpdated',
'isManual', 'maturityDate', 'nickname', 'status', 'accountType', 
'homeInsuranceType', 'interestRate', 'lifeInsuranceType', 'providerID',
'providerName', 'policyStatus', 'premiumPaymentTerm', 'term', 
'enrollmentDate', 'primaryRewardUnit', 'currentLevel', 'nextLevel', 
'lastEmployeeContributionDate', 'providerAccountID']

HoldingNestedModels = ['costBasis', 'holdingPrice', 'unvestedValue', 'value', 
'vestedValue', 'employeeContribution', 'employerContribution', 'parValue',
'spread', 'strikePrice']

HoldingFeatures = ['accountID', 'cusipNumber', 'description', 'holdingType',
'quantity', 'symbol', 'unvestedQuantity', 'vestedQuantity', 'vestedSharesExercisable',
'vestingDate', 'contractQuantity', 'couponRate', 'currencyType', 
'exercisedQuantity', 'expiratinDate', 'grantDate', 'interestRate', 
'maturityDate', 'optionType', 'term', 'providerAccountID']

InvestmentOptionNestedModels = ['optionPrice', 'grossExpenseAmount', 'netExpenseAmount']
InvestmentOptionFeatures = ['optionID', 'cusipNumber', 'description',
'fiveYearReturn', 'isin', 'oneMonthReturn', 'oneYearReturn', 'priceAsOfDate',
'sedol', 'symbol', 'tenYearReturn', 'threeMonthReturn', 'inceptionToDateReturn', 
'yearToDateReturn', 'inceptionDate', 'grossExpenseRatio', 'netExpenseRatio']

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
	account401kLoan = MoneySerializer(required=False, many=True)
	accountAmountDue = MoneySerializer(required=False, many=True)
	annuityBalance = MoneySerializer(required=False, many=True)
	availableBalance = MoneySerializer(required=False, many=True)
	availableCash = MoneySerializer(required=False, many=True)
	availableCredit = MoneySerializer(required=False, many=True)
	availableLoan = MoneySerializer(required=False, many=True)
	accountBalance = MoneySerializer(required=False, many=True)
	cash = MoneySerializer(required=False, many=True)
	cashValue = MoneySerializer(required=False, many=True)
	currentBalance = MoneySerializer(required=False, many=True)
	faceAmount = MoneySerializer(required=False, many=True)
	lastPayment = MoneySerializer(required=False, many=True)
	accountLastPaymentAmount = MoneySerializer(required=False, many=True)
	marginBalance = MoneySerializer(required=False, many=True)
	maturityAmount = MoneySerializer(required=False, many=True)
	minimumAmountDue = MoneySerializer(required=False, many=True)
	moneyMarketBalance = MoneySerializer(required=False, many=True)
	accountRefreshInfo = RefreshInfoSerializer(many=True)
	runningBalance = MoneySerializer(required=False, many=True)
	totalCashLimit = MoneySerializer(required=False, many=True)
	totalCreditLine = MoneySerializer(required=False, many=True)
	totalUnvestedBalance = MoneySerializer(required=False, many=True)
	totalVestedBalance = MoneySerializer(required=False, many=True)
	escrowBalance = MoneySerializer(required=False, many=True)
	originalLoanAmount = MoneySerializer(required=False, many=True)
	principalBalance = MoneySerializer(required=False, many=True)
	recurringPayment = MoneySerializer(required=False, many=True)
	totalCreditLimit = MoneySerializer(required=False, many=True)
	rewardBalance = RewardBalanceSerializer(required=False, many=True)
	shortBalance = MoneySerializer(required=False, many=True)
	lastEmployeeContributionAmount = MoneySerializer(required=False, many=True)


	class Meta:
		model = YodleeAccount
		fields = '__all__'

	def create(self, validated_data):
		subModels = {}
		for item in YodleeAccountNestedModels:
			if item in validated_data:
				subModels[item] = validated_data.pop(item)

		yodleeAccount = YodleeAccount.objects.create(**validated_data)

		for item in subModels:
			getattr(data.models, item[0].upper() + item[1:]).objects.create(
				yodleeAccount=yodleeAccount,
				**subModels[item])

		return yodleeAccount

	def update(self, instance, validated_data):
		modelsToUpdate = {}
		for item in YodleeAccountNestedModels:
			if item in validated_data:
				modelsToUpdate[item] = validated_data.pop(item)

		for item in YodleeAccountFeatures:
			if item in validated_data:
				setattr(instance, item, validated_data.get(item, getattr(instance, item)))

		for item in modelsToUpdate:
			getattr(data.models, item[0].upper() + item[1:]).objects.create(
				yodleeAccount=instance,
				**modelsToUpdate[item])

		return instance


class UserDataSerializer(serializers.ModelSerializer):
	yodleeAccount = YodleeAccountSerializer(required=False)
	class Meta:
		model = UserData 
		fields = '__all__'

class HoldingSerializer(serializers.ModelSerializer):
	costBasis = MoneySerializer(required=False, many=True)
	holdingPrice = MoneySerializer(required=False, many=True)
	unvestedValue = MoneySerializer(required=False, many=True)
	value = MoneySerializer(required=False, many=True)
	vestedValue = MoneySerializer(required=False, many=True)
	employeeContribution = MoneySerializer(required=False, many=True)
	employerContribution = MoneySerializer(required=False, many=True)
	parValue = MoneySerializer(required=False, many=True)
	spread = MoneySerializer(required=False, many=True)
	strikePrice = MoneySerializer(required=False, many=True)

	class Meta:
		model = Holding 
		fields = '__all__'

	def create(self, validated_data):
		subModels = {}
		for item in HoldingNestedModels:
			if item in validated_data:
				subModels[item] = validated_data.pop(item)

		holding = Holding.objects.create(**validated_data)

		for item in subModels:
			getattr(data.models, item[0].upper() + item[1:]).objects.create(
				holding=holding, 
				**subModels[item])

		return holding

	def update(self, instance, validated_data):
		modelsToUpdate = {}
		for item in HoldingNestedModels:
			if item in validated_data:
				modelsToUpdate[item] = validated_data.pop(item)

		for item in HoldingFeatures:
			if item in validated_data:
				setattr(instance, item, validated_data.get(item, getattr(instance, item)))

		for item in modelsToUpdate:
			getattr(data.models, item[0].upper() + item[1:]).objects.create(
				holding=instance,
				**modelsToUpdate[item])

		return instance

class AssetClassificationSerializer(serializers.ModelSerializer):

	class Meta:
		model = AssetClassification 
		fields = '__all__'

class HistoricalBalanceSerializer(serializers.ModelSerializer):
	balance = MoneySerializer(required=False, many=True)
	class Meta:
		model = HistoricalBalance 
		fields = '__all__'

	def create(self, validated_data):
		if 'balance' in validated_data:
			balance_data = validated_data.pop('balance')
			historicalBalance = HistoricalBalance.objects.create(**validated_data)
			Balance.objects.create(historicalBalance=historicalBalance, **balance_data)

			return historicalBalance
		else:
			historicalBalance = HistoricalBalance.objects.create(**validated_data)

			return historicalBalance

class InvestmentPlanSerializer(serializers.ModelSerializer):

	class Meta:
		model = InvestmentPlan 
		fields = '__all__'

class InvestmentOptionSerializer(serializers.ModelSerializer):
	optionPrice = MoneySerializer(required=False, many=True)
	grossExpenseAmount = MoneySerializer(required=False, many=True)
	netExpenseAmount = MoneySerializer(required=False, many=True)
	
	class Meta:
		model = InvestmentOption 
		fields = '__all__'

	def create(self, validated_data):
		subModels = {}
		for item in InvestmentOptionNestedModels:
			if item in validated_data:
				subModels[item] = validated_data.pop(item)

		investmentOption = InvestmentOption.objects.create(**validated_data)

		for item in subModels:
			getattr(data.models, item[0].upper() + item[1:]).objects.create(
				investmentOption=investmentOption,
				**subModels[item])

		return investmentOption

	def update(self, instance, validated_data):
		modelsToUpdate = {}
		for item in InvestmentOptionNestedModels:
			if item in validated_data:
				modelsToUpdate[item] = validated_data.pop(item)

		for item in InvestmentOptionFeatures:
			if item in validated_data:
				setattr(instance, item, validated_data.get(item, getattr(instance, item)))

		for item in modelsToUpdate:
			getattr(data.models, item[0].upper() + item[1:]).objects.create(
				investmentOption=instance,
				**modelsToUpdate[item])

		return instance