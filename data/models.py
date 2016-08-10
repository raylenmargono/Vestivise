from django.db import models
from account.models import UserProfile


#### USER DATA MODELS
class UserData(models.Model):

    userProfile = models.OneToOneField(
        UserProfile,
        related_name='data',
        )
    class Meta:
        verbose_name = "UserData"
        verbose_name_plural = "UserData"

    def __str__(self):
        return "%s %s" % (self.userProfile.firstName, self.userProfile.lastName)

##### YODLEE MODELS CONNECTED TO USERDATA #####

##NOTE: THESE FIELDS ARE VERY LIKELY TO CHANGE

### PLEASE READ THIS BEFORE GOING FARTHER:
### THESE ARE NEAR-COPIES FROM THE YODLEE API
### DATA MODEL DOCUMENTATION, AVAILABLE AT
### https://developer.yodlee.com/Yodlee_API/Data_Model
### YODLEE EXCLUSIVELY USES STRINGS AND TYPES 
### FOR THEIR MODELS, WHLIE WE USE THE ACTUAL
### VALUES ASSOCIATED WITH EACH MODEL. 
### SOME FIELDS USE ENUMERATED TYPES, THEY ARE
### AVAILABLE ON THE ABOVE PAGE. WE ACCEPT THEM
### IN THEIR CHARACTER FORM INSTEAD OF THEIR
### INTEGER FORM. 

### Comments of structure [item1, item2] describe
### the fact that this field is conditionally present
### depending on the category or 'container' of the 
### instance of the respective model.

### If this is an enumerated type, there will be a 
### comment "E" to its right, values of the 
### enumerated type can be found on the above page.

### Commented names in the place of a field relate 
### to a separate model which shares a one to one
### or many to one relationship with this model. 
### Note that these are lowercase to maintain naming
### conventions with other fields.

### Field names that unfortunately share a name with
### a basic python function, object, etc, will have an
### underscore '_' at the beginning of their name. 
### For example, 'id' is a very common name that is also
### a basic python function, this is to be replaced with
### '_id'

##### HOW IS THIS STRUCTURED
### PRIMARY MODELS:
### - YodleeAccounts
### - Holdings
### - AssetClassification
### - HistoricalBalances
### - InvestmentPlan
### - InvestmentOptions
### ACCESSORY MODELS: (Models that fit into the original models)
### - General Use Models
### - YodleeAccounts
### - Holdings
### - HistoricalBalances
### - InvestmentOptions
### CONVENIENCE MODELS


### YODLEE ACCOUNTS 
#NOTE: Rename to avoid conflict with other account model?
#ADDITIONAL NOTE; This has a massive amount of conditional
#fields based on the container. An exhausting amount. 
#Let me know your thoughts on whether you want this broken
#into additional tables. We'll wee what we can do.
#Also, if you think any fields are useless, I will be
#more than delighted to remove them.
class YodleeAccount(models.Model):
    userData = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        related_name='yodleeAccounts',
        )
    createdAt = models.DateTimeField(auto_now_add=True)

    accountID = models.BigIntegerField()
    #account401kLoan (Money) [investment]
    accountName = models.CharField(max_length=40, blank=True, null=True)
    accountNumber = models.CharField(max_length = 20, blank=True, null=True)
    #accountAmountDue (Money) [bill, creditCard, insurance, loan]
    #annuityBalance (Money) [insurance, investment]
    apr = models.FloatField(blank=True, null=True) #[creditCard]
    isAsset = models.BooleanField()
    #availableBalance (Money) [bank]
    #availableCash (Money) [creditCard]
    #availableCredit(Money) [creditCard, loan]
    #availableLoan (Money) [investment]
    #accountBalance (Money) [bank, creditCard, investment, insurance, loan, bill]
    #cash (Money) [investment]
    #cashValue (Money) [insurance]
    classification = models.CharField(max_length=14, blank=True, null=True)#E [bank, creditCard, investment]
    container = models.CharField(max_length=25)
    #currentBalance (Money) [bank]
    dueDate = models.DateField(blank=True, null=True) #[bill, creditCard, insurance, loan]
    expirationDate = models.DateField(blank=True, null=True) #[insurance]
    #faceAmount (Money) #[insurance]
    interestRate = models.FloatField(blank=True, null=True) #[bank, loan]
    #lastPayment (Money) [bill]
    #accountLastPaymentAmount (Money) [creditCard, insurance, bill, loan]
    lastPaymentDate = models.DateField(blank=True, null=True)
    lastUpdated = models.DateTimeField(blank=True, null=True)
    lastHoldingsUpdate = models.DateTimeField(auto_now=True)
    isManual = models.BooleanField(default=False)
    #marginBalance (Money) [investment]
    #maturityAmount (Money) [bank]
    maturityDate = models.DateField(blank=True, null=True)# [bank, loan]
    #minimumAmountDue (Money) [creditCard, insurance, bill, loan]
    #moneyMarketBalance (Money) [investment]
    nickname = models.CharField(max_length=40, blank=True, null=True)
    #accountRefreshInfo (RefreshInfo)
    #runningBalance (Money) [creditCard]
    status = models.CharField(max_length=12, blank=True, null=True) #E
    #totalCashLimit (Money) [creditCard]
    #totalCreditLine (Money) [creditCard]
    #totalUnvestedBalance (Money) [investment]
    #totalVestedBalance (Money) [investment]
    accountType = models.CharField(max_length=40, blank=True, null=True)#[investment, insurance, bill, loan, bank, creditCard]
    #escrowBalance (Money) [loan]
    homeInsuranceType = models.CharField(max_length=30, blank=True, null=True)#E (But undocumented?) [insurance]
    interestRate = models.FloatField(blank=True, null=True)# [bank]
    lifeInsuranceType = models.CharField(max_length=30, blank=True, null=True)#E (But undocumented?) [insurance]
    #originalLoanAmount(Money) [loan]
    providerID = models.PositiveIntegerField(blank=True, null=True)
    providerName = models.CharField(max_length=40, blank=True, null=True)
    #principalBalance (Money) [loan]
    policyStatus = models.CharField(max_length=30, blank=True, null=True)#E (But undocumented?) [insurance]
    premiumPaymentTerm = models.PositiveIntegerField(blank=True, null=True)# [insurance]
    #recurringPayment (Money) [loan]
    term = models.TextField(blank=True, null=True)# [bank, loan]
    ## NOTE: No idea on how the above is structured.
    ## will revamp when I have an actual example. We
    ## will just accept the string for now.
    #totalCreditLimit (Money) [loan]
    enrollmentDate = models.DateField(blank=True, null=True)#[reward]
    primaryRewardUnit = models.CharField(max_length=25, blank=True, null=True)#[reward]
    #rewardBalance (RewardBalance) [reward]
    currentLevel = models.CharField(max_length=20, blank=True, null=True)#[reward]
    nextLevel = models.CharField(max_length=20, blank=True, null=True)#[reward]
    #shortBalance (Money) [investment]
    #holderProfile (I'm going to leave this one out, since 
    #I feel its purpose is fulfilled by the UserData/UserProfile)
    #lastEmployeeContributionAmount (Money) [investment]
    lastEmployeeContributionDate = models.DateField(blank=True, null=True) #[investment]
    providerAccountID = models.BigIntegerField(blank=True, null=True) #[bank, creditCard, insurance, loan, bill, investment]
    updatedAt = models.DateTimeField(auto_now_add=True)


### YODLEE HOLDINGS

class Holding(models.Model):
    yodleeAccount = models.ForeignKey(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='holdings'
        )

    accountID = models.BigIntegerField()
    #costBasis (Money)
    cusipNumber = models.CharField(max_length=9, blank=True, null=True)
    createdAt = models.DateTimeField()
    description = models.CharField(max_length=30, blank=True, null=True)
    holdingType = models.CharField(max_length=20, blank=True, null=True)
    #holdingPrice (Money)
    quantity = models.PositiveIntegerField(blank=True, null=True)
    symbol = models.CharField(max_length=20, blank=True, null=True)
    unvestedQuantity = models.PositiveIntegerField(blank=True, null=True)#[EMPLOYEE_STOCK_OPTION]
    #unvestedValue (Money) [EMPLOYEE_STOCK_OPTION]
    #value (Money) [EMPLOYEE_STOCK_OPTION]
    vestedQuantity = models.PositiveIntegerField(blank=True, null=True)#[EMPLOYEE_STOCK_OPTION]
    vestedSharesExercisable = models.PositiveIntegerField(blank=True, null=True)#[EMPLOYEE_STOCK_OPTION]
    #vestedValue (Money) [EMPLOYEE_STOCK_OPTION]
    vestingDate = models.DateField(blank=True, null=True) #[EMPLOYEE_STOCK_OPTION]
    contractQuantity = models.PositiveIntegerField(blank=True, null=True) #[Commodity]
    couponRate = models.FloatField(blank=True, null=True) #[Bond]
    currencyType = models.CharField(max_length=20, blank=True, null=True)
    #employeeContribution (Money) [Employee_Stock_Option]
    #employerContribution (Money) [Employee_Stock_Option]
    exercisedQuantity = models.PositiveIntegerField(blank=True, null=True)#[Employee_Stock_Option]
    expirationDate = models.DateField(blank=True, null=True)#[Option, Future, Commodity]
    grantDate = models.DateField(blank=True, null=True)#[Employee_Stock_Option]
    interestRate = models.FloatField(blank=True, null=True)#[CD]
    maturityDate = models.DateField(blank=True, null=True)#[CD, Bond]
    optionType = models.CharField(max_length=20, blank=True, null=True)#E, call or put [Option]
    #parValue (Money) [Bond]
    #spread (Money) [Employee_Stock_Option]
    #strikePrice (Money) [Employee_Stock_Option]
    term = models.TextField(blank=True, null=True)#[CD]
    ##NOTE: I believe that the term field handles a time delta
    ## not yet sure if it contains the end or whatever. We can
    ## probably use a django duration field to store it. Will
    ## currently just store the raw string until I can fix it.
    providerAccountID = models.BigIntegerField(blank=True, null=True)#[bank, creditCard, insurance, loan, bill, investment]


    def __str__(self):
        return "%s" % (self.holdingType)

### YODLEE ASSETCLASSIFICATION

class AssetClassification(models.Model):
    holding = models.ForeignKey(
        Holding,
        on_delete=models.CASCADE,
        related_name='assetClassifications'
        )
    classificationType = models.CharField(max_length=10)#E (assetClass, country, sector, style)
    classificationValue = models.CharField(max_length=30)#E
    allocation = models.FloatField()

### YODLEE HISTORICALBALANCES

class HistoricalBalance(models.Model):
    yodleeAccount = models.ForeignKey(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='historicalBalances'
        )
    date = models.DateField()
    asOfDate = models.DateField()
    #balance (Money)
    isAsset = models.BooleanField()

### YODLEE INVESTMENTPLAN

class InvestmentPlan(models.Model):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='investmentPlan'
        )
    planID = models.BigIntegerField()
    name = models.CharField(max_length=40, blank=True, null=True)
    number = models.BigIntegerField(blank=True, null=True)
    provider = models.CharField(max_length=40, blank=True, null=True)
    asOfDate = models.DateField()
    returnAsOfDate = models.DateField()
    feesAsOfDate = models.DateField()

### YODLEE INVESTMENTOPTION

class InvestmentOption(models.Model):
    yodleeAccount = models.ForeignKey(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='investmentOptions'
        )
    optionID = models.BigIntegerField()
    cusipNumber = models.CharField(max_length=9, blank=True, null=True)
    description = models.CharField(max_length=40, blank=True, null=True)
    #historicReturns (HistoricReturns)
    holdingType = models.CharField(max_length=20, blank=True, null=True)
    isin = models.CharField(max_length=12, blank=True, null=True)
    #optionPrice (Money)
    priceAsOfDate = models.DateField(blank=True, null=True)
    sedol = models.CharField(max_length=7, blank=True, null=True)
    symbol = models.CharField(max_length=5, blank=True, null=True)
    inceptionToDateReturn = models.FloatField(blank=True, null=True)
    yearToDateReturn = models.FloatField(blank=True, null=True)
    inceptionDate = models.DateField(blank=True, null=True)
    grossExpenseRatio = models.FloatField(blank=True, null=True)
    #grossExpenseAmount (Money)
    netExpenseRatio = models.FloatField(blank=True, null=True)
    #netExpenseAmount (Money)

### YODLEE ACCESSORY MODELS (MODELS THAT APPEAR IN PRIMARY MODELS)
### GENERAL USE MODELS
class Money(models.Model):
    amount = models.FloatField()
    currency = models.CharField(max_length=3)

class RefreshInfo(models.Model):
    statusCode = models.PositiveSmallIntegerField()
    #There are a lot of status codes
    #https://developer.yodlee.com/Yodlee_API/Status_Codes
    #https://developer.yodlee.com/FAQs/Error_Codes
    statusMessage = models.CharField(max_length=40, blank=True, null=True)
    status = models.CharField(max_length=40, blank=True, null=True)
    #Also, the statuses can be really longwinded.
    additionalStatus = models.CharField(max_length=40, blank=True, null=True)
    nextRefreshScheduled = models.DateTimeField()
    lastRefreshed = models.DateTimeField()
    lastRefreshAttempt = models.DateTimeField()
    actionRequested = models.CharField(max_length=20, blank=True, null=True)
    #Action Requested will read 'UPDATE_CREDENTIALS'
    #if the provider account needs an action to be taken
    #due to erros. This field is not available in the
    #response for refresh and provider endpoint APIs
    message = models.TextField(blank=True, null=True)

class RewardBalance(models.Model):
    description = models.TextField(blank=True, null=True)
    balance = models.PositiveIntegerField()
    units = models.CharField(max_length=30, blank=True, null=True)
    balanceType = models.CharField(max_length=20, blank=True, null=True)#E
    expiryDate = models.DateField()
    balanceToLevel = models.PositiveIntegerField(blank=True, null=True)
    balanceToReward = models.PositiveIntegerField(blank=True, null=True)

### YODLEE ACCOUNTS
class Account401kLoan(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name ='account401kLoan',
        )

class AccountAmountDue(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='accountAmountDue',
        )

class AnnuityBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='annuityBalance'
        )

class AvailableBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='availableBalance',
        )

class AvailableCash(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='availableCash',
        )

class AvailableCredit(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='availableCredit',
        )

class AvailableLoan(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='availableLoan',
        )

class AccountBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='accountBalance',
        )

class Cash(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='cash',
        )

class CashValue(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='cashValue',
        )

class CurrentBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='currentBalance',
        )

class FaceAmount(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='faceAmount',
        )

class LastPayment(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='lastPayment',
        )

class AccountLastPaymentAmount(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='accountLastPayment',
        )

class MarginBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='marginBalance',
        )

class MatuityAmount(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='maturityAmount',
        )

class MinimumAmountDue(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='minimumAmountDue',
        )

class MoneyMarketBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='moneyMarketBalance',
        )

class AccountRefreshInfo(RefreshInfo):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='accountRefreshInfo',
        )

class RunningBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='runningBalance',
        )

class TotalCashLimit(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='totalCashLimit',
        )

class TotalCreditLine(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='totalCreditLine',
        )

class TotalUnvestedBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='totalUnvestedBalance',
        )

class TotalVestedBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='totalVestedBalance',
        )

class EscrowBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='escrowBalance',
        )

class OriginalLoanAmount(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='originalLoanAmount',
        )

class PrincipalBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='principalBalance',
        )

class RecurringPayment(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='recurringPayment',
        )

class TotalCreditLimit(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='totalCreditLimit',
        )

class AccountRewardBalance(RewardBalance):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='accountRewardBalance',
        )

class ShortBalance(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='shortBalance',
        )

class LastEmployeeContributionAmount(Money):
    yodleeAccount = models.OneToOneField(
        YodleeAccount,
        on_delete=models.CASCADE,
        related_name='lastEmployeeContributionAmount',
        )

### YODLEE HOLDINGS

class CostBasis(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='costBasis',
        )

class HoldingPrice(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='holdingPrice',
        )

class UnvestedValue(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='unvestedValue',
        )

class Value(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='value',
        )

class VestedValue(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='vestedValue',
        )

class EmployeeContribution(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='employeeContribution',
        )

class EmployerContribution(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='employerContribution',
        )

class ParValue(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='parValue',
        )

class Spread(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='spread',
        )

class StrikePrice(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        related_name='strikePrice'
        )

### YODLEE HISTORICALBALANCES

class Balance(Money):
    historicalBalance = models.OneToOneField(
        HistoricalBalance,
        on_delete=models.CASCADE,
        related_name='balance',
        )

### YODLEE INVESTMENTOPTION

class HistoricReturns(models.Model):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        related_name='historicReturns',
        )
    oneMonthReturn = models.FloatField()
    threeMonthReturn = models.FloatField()
    oneYearReturn = models.FloatField()
    threeYearReturn = models.FloatField()
    fiveYearReturn = models.FloatField()
    tenYearReturn = models.FloatField()

class OptionPrice(Money):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        related_name='optionPrice',
        )

class GrossExpenseAmount(Money):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        related_name='grossExpenseAmount',
        )

class NetExpenseAmount(Money):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        related_name='netExpenseAmount',
        )

### ACCESSORY MODELS (MODELS FOR CONVENIENCE)

class Security(models.Model):
    symbol = models.CharField(max_length=5, primary_key=True)
    lastUpdated = models.DateField()

    def __str__(self):
        return self.symbol

class SecurityPrice(models.Model):
    stock = models.ForeignKey(
        Security,
        on_delete=models.CASCADE,
        related_name='securityPrice'
        )
    date = models.DateField()
    price = models.DecimalField(max_digits=11, decimal_places=6)

    def __str__(self):
        return "%s %s" % (self.stock.symbol, str(self.date))