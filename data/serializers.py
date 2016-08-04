from rest_framework import serializers
from data.models import *
import data
from collections import OrderedDict
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.fields import SkipField, set_value

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

InvestmentPlanFeatures = ['planID', 'name', 'number', 
'provider', 'asOfDate', 'returnAsOfDate', 'feesAsOfDate']

InvestmentOptionNestedModels = ['optionPrice', 'grossExpenseAmount', 'netExpenseAmount']
InvestmentOptionFeatures = ['optionID', 'cusipNumber', 'description',
'fiveYearReturn', 'isin', 'oneMonthReturn', 'oneYearReturn', 'priceAsOfDate',
'sedol', 'symbol', 'tenYearReturn', 'threeMonthReturn', 'inceptionToDateReturn', 
'yearToDateReturn', 'inceptionDate', 'grossExpenseRatio', 'netExpenseRatio']

## Yodlee to internal names.

YodleeAccountNames = {'401kLoan':'account401kLoan', 'amountDue':'accountAmountDue',
 'balance':'accountBalance', 'CONTAINER':'container', 'id':'accountID',
 'lastPaymentAmount':'accountLastPaymentAmount', 'providerId':'providerID',
 'providerAccountId':'providerAccountID', 'accountStatus':'status',
 'Term':'term', 'refreshinfo':'accountRefreshInfo'}

HoldingNames = {'accountId':'accountID', 'price':'holdingPrice',
 'providerAccountId':'providerAccountID'}

AssetClassificationNames = {'Allocation':'allocation'}

InvestmentPlanNames = {'planId':'planID'}

InvestmentOptionNames = {'optionId':'optionID'}

def natural_to_internal_value(self, data):
    if not isinstance(data, dict):
        message = self.error_messages['invalid'].format(
            datatype=type(data).__name__
        )
        raise ValidationError({
            api_settings.NON_FIELD_ERRORS_KEY: [message]
        })

    ret = OrderedDict()
    errors = OrderedDict()
    fields = self._writable_fields

    for field in fields:
        validate_method = getattr(self, 'validate_' + field.field_name, None)
        primitive_value = field.get_value(data)
        try:
            validated_value = field.run_validation(primitive_value)
            if validate_method is not None:
                validated_value = validate_method(validated_value)
        except ValidationError as exc:
            errors[field.field_name] = exc.detail
        except DjangoValidationError as exc:
            errors[field.field_name] = list(exc.messages)
        except SkipField:
            pass
        else:
            set_value(ret, field.source_attrs, validated_value)

    if errors:
        raise ValidationError(errors)

    return ret

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

class AssetClassificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssetClassification 
        fields = '__all__'

    def to_internal_value(self, data):
        for item in data:
            if item in AssetClassification:
                data[AssetClassificationNames[item]] = data.pop(item)
        return natural_to_internal_value(self, data)

class HistoricalBalanceSerializer(serializers.ModelSerializer):
    balance = MoneySerializer(required=False)
    class Meta:
        model = HistoricalBalance 
        fields = '__all__'

    def create(self, validated_data):
        subModels = {}
        if 'balance' in validated_data:
            subModels['balance'] = validated_data.pop('balance')

        historicalBalance = HistoricalBalance.objects.create(**validated_data)

        for item in subModels:
            getattr(data.models, item).objects.create(
                historicalBalance=historicalBalance,
                **subModels[item])

        return historicalBalance

    def update(self, instance, validated_data):
        modelsToUpdate = {}

        if 'balance' in validated_data:
            modelsToUpdate['balance'] = validated_data.pop('balance')

        for item in ['date', 'asOfDate', 'isAsset']:
            if item in validated_data:
                setattr(instance, item, validated_data.get(item, getattr(instance, item)))

        instance.save()

        for item in modelsToUpdate:
            getattr(instance, item).delete()
            getattr(data.models, item[0].upper() + item[1:]).objects.create(
                historicalBalance=instance,
                **modelsToUpdate[item])

        return instance

class InvestmentPlanSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvestmentPlan 
        fields = '__all__'

    def create(self, validated_data):
        for item in validated_data:
            if item in InvestmentPlanNames:
                validated_data[investmentPlanNames[item]] = validated_data.pop(item)

        investmentPlan = InvestmentPlan.objects.create(**validated_data)

        return investmentPlan

    def update(self, instance, validated_data):

        for item in validated_data:
            if item in InvestmentPlanNames:
                validated_data[investmentPlanNames[item]] = validated_data.pop(item)

        for item in InvestmentPlanFeatures:
            if item in validated_data:
                setattr(instance, item, validated_data.get(item, getattr(instance, item)))

        return investmentPlan

    def to_internal_value(self, data):
        for item in data:
            if item in InvestmentPlanNames:
                data[InvestmentPlanNames[item]] = data.pop(item)
        return natural_to_internal_value(self, data)


class InvestmentOptionSerializer(serializers.ModelSerializer):
    optionPrice = MoneySerializer(required=False)
    grossExpenseAmount = MoneySerializer(required=False)
    netExpenseAmount = MoneySerializer(required=False)
    
    class Meta:
        model = InvestmentOption 
        fields = '__all__'

    def create(self, validated_data):
        for item in validated_data:
            if item in InvestmentOptionNames:
                validated_data[investmentOptionNames[item]] = validated_data.pop(item)
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
        for item in validated_data:
            if item in InvestmentOptionNames:
                validated_data[investmentOptionNames[item]] = validated_data.pop(item)
        modelsToUpdate = {}
        for item in InvestmentOptionNestedModels:
            if item in validated_data:
                modelsToUpdate[item] = validated_data.pop(item)

        for item in InvestmentOptionFeatures:
            if item in validated_data:
                setattr(instance, item, validated_data.get(item, getattr(instance, item)))

        instance.save()

        for item in modelsToUpdate:
            getattr(data.models, item[0].upper() + item[1:]).objects.create(
                investmentOption=instance,
                **modelsToUpdate[item])

        return instance

    def to_internal_value(self, data):
        for item in data:
            if item in InvestmentOptionNames:
                data[YodleeAccountNames[item]] = data.pop(item)
        return natural_to_internal_value(self, data)

class HoldingSerializer(serializers.ModelSerializer):
    #Sub Money Models
    costBasis = MoneySerializer(required=False)
    holdingPrice = MoneySerializer(required=False)
    unvestedValue = MoneySerializer(required=False)
    value = MoneySerializer(required=False)
    vestedValue = MoneySerializer(required=False)
    employeeContribution = MoneySerializer(required=False)
    employerContribution = MoneySerializer(required=False)
    parValue = MoneySerializer(required=False)
    spread = MoneySerializer(required=False)
    strikePrice = MoneySerializer(required=False)
    #Sub Primary Models
    assetClassification = AssetClassificationSerializer(required=False, many=True)

    class Meta:
        model = Holding 
        fields = '__all__'

    def create(self, validated_data):
        for item in validated_data:
            if item in HoldingNames:
                validated_data[HoldingNames[item]] = validated_data.pop(item)
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
        for item in validated_data:
            if item in HoldingNames:
                validated_data[HoldingNames[item]] = validated_data.pop(item)
        modelsToUpdate = {}
        for item in HoldingNestedModels:
            if item in validated_data:
                modelsToUpdate[item] = validated_data.pop(item)

        for item in HoldingFeatures:
            if item in validated_data:
                setattr(instance, item, validated_data.get(item, getattr(instance, item)))

        instance.save()

        for item in modelsToUpdate:
            getattr(instance, item).delete()
            getattr(data.models, item[0].upper() + item[1:]).objects.create(
                holding=instance,
                **modelsToUpdate[item])

        return instance

    def to_internal_value(self, data):
        for item in data:
            if item in HoldingNames:
                data[HoldingNames[item]] = data.pop(item)
        return natural_to_internal_value(self, data)

class YodleeAccountSerializer(serializers.ModelSerializer):
    account401kLoan = MoneySerializer(required=False)
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
    faceAmount = MoneySerializer(required=False)
    lastPayment = MoneySerializer(required=False)
    accountLastPaymentAmount = MoneySerializer(required=False)
    marginBalance = MoneySerializer(required=False)
    maturityAmount = MoneySerializer(required=False)
    minimumAmountDue = MoneySerializer(required=False)
    moneyMarketBalance = MoneySerializer(required=False)
    accountRefreshInfo = RefreshInfoSerializer()
    runningBalance = MoneySerializer(required=False)
    totalCashLimit = MoneySerializer(required=False)
    totalCreditLine = MoneySerializer(required=False)
    totalUnvestedBalance = MoneySerializer(required=False)
    totalVestedBalance = MoneySerializer(required=False)
    escrowBalance = MoneySerializer(required=False)
    originalLoanAmount = MoneySerializer(required=False)
    principalBalance = MoneySerializer(required=False)
    recurringPayment = MoneySerializer(required=False)
    totalCreditLimit = MoneySerializer(required=False)
    rewardBalance = RewardBalanceSerializer(required=False)
    shortBalance = MoneySerializer(required=False)
    lastEmployeeContributionAmount = MoneySerializer(required=False)

    holding = HoldingSerializer(required=False, many=True)
    historicalBalance = HistoricalBalanceSerializer(required=False, many=True)
    investmentPlan = InvestmentPlanSerializer(required=False)
    investmentOption = InvestmentOptionSerializer(required=False, many=True)

    class Meta:
        model = YodleeAccount
        fields = '__all__'

    def create(self, validated_data):
        for item in validated_data:
            if item in YodleeAccountNames:
                validated_data[YodleeAccountNames[item]] = validated_data.pop(item)
        print (validated_data)
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
        for item in validated_data:
            if item in YodleeAccountNames:
                validated_data[YodleeAccountNames[item]] = validated_data.pop(item)
        modelsToUpdate = {}
        for item in YodleeAccountNestedModels:
            if item in validated_data:
                modelsToUpdate[item] = validated_data.pop(item)

        for item in YodleeAccountFeatures:
            if item in validated_data:
                setattr(instance, item, validated_data.get(item, getattr(instance, item)))

        instance.save()

        for item in modelsToUpdate:
            getattr(instance, item).delete()
            getattr(data.models, item[0].upper() + item[1:]).objects.create(
                yodleeAccount=instance,
                **modelsToUpdate[item])

        return instance

    def to_internal_value(self, data):
        for item in data:
            if item in YodleeAccountNames:
                data[YodleeAccountNames[item]] = data.pop(item)
        return natural_to_internal_value(self, data)

class UserDataSerializer(serializers.ModelSerializer):
    yodleeAccount = YodleeAccountSerializer(required=False, many=True)
    class Meta:
        model = UserData 
        fields = '__all__'

    def create(self, validated_data):
        subModels = {}
        if 'yodleeAccount' in validated_data:
            subModels['yodleeAccount'] = validated_data.pop('yodleeAccount')

        userData = UserData.objects.create(**validated_data)

        for item in subModels:
            getattr(data.models, item[0].upper() + item[1:]).objects.create(
                userData=userData,
                **subModels[item])

        return userData

    def update(self, instance, validated_data):
        if 'yodleeAccount' in validated_data:
            yodleeAccount_data = validated_data.pop('yodleeAccount')
            YodleeAccount.objects.create(userData=instance, **yodleeAccount_data)
            return instance
        else:
            return instance



