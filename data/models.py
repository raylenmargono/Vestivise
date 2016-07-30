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
### - Provider
### - ProviderAccounts
### - Accounts
### - RewardBalances
### - Transactions
### - Transaction Category
### - Holdings
### - AssetClassification
### - HistoricalBalances
### - InvestmentPlan
### - InvestmentOptions
### - Statements
### ACCESSORY MODELS: (Models that fit into the original models)
### - General Use Models
### - Provider
### - ProviderAccounts
### - Accounts
### - Transactions
### - Holdings
### - HistoricalBalances
### - InvestmentOptions
### - Statements
### CONVENIENCE MODELS

### YODLEE PROVIDER
class Provider(models.Model):
    _id = models.BigIntegerField()
    name = models.CharField(max_length=30, blank=True)
    loginURL = models.URLField(blank=True)
    baseURL = models.URLField(blank=True)
    favicon = models.URLField(blank=True)
    logo = models.URLField(blank=True)
    status = models.CharField(max_length=30, blank=True)
    #containerNames
    mfaType = models.CharField(max_length=17, blank=True)#E
    phelp = models.TextField(blank=True)
    oAuthSite = models.BooleanField(blank=True)
    lastModified = models.DateTimeField(blank=True)
    forgotPasswordURL = models.URLField(blank=True)
    loginHelp = models.TextField(blank=True)
    primaryLanguageISOCode = models.CharField(max_length=2, blank=True)
    availableFrom = models.DateTimeField(blank=True)
    #loginform
    ##NOTE I know you're opposed to JSONFields, and I've typed up 
    ##a loginform in the below models based on the example one Yodlee provides
    ##But I'm not sure if that's the standard, and whether or not they'll be 
    ##structured the same over services. That tempts me towards a JSONField, but
    ##we'll pray that they're all similar for right now. 


### YODLEE PROVIDERACCOUNTS
class ProviderAccounts(models.Model):

    _id = models.BigIntegerField()
    providerAccountID = models.BigIntegerField()
    aggregationSource = models.CharField(max_length=13) #E
    #aggreagationSource is an enum of values USER or PRE_POPULATED
    #ProviderRefrehsInfo (RefreshInfo)

### YODLEE ACCOUNTS 
#NOTE: Rename to avoid conflict with other account model?
#ADDITIONAL NOTE; This has a massive amount of conditional
#fields based on the container. An exhausting amount. 
#Let me know your thoughts on whether you want this broken
#into additional tables. We'll wee what we can do.
#Also, if you think any fields are useless, I will be
#more than delighted to remove them.
class Account(models.Model):
    userData = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        )
    _id = models.BigIntegerField()
    #401kLoan (Money) [investment]
    accountName = models.CharField(max_length=40, blank=True)
    accountNumber = models.BigIntegerField(blank=True)
    #accountAmountDue (Money) [bill, creditCard, insurance, loan]
    #annuityBalance (Money) [insurance, investment]
    apr = models.FloatField(blank=True) #[creditCard]
    isAsset = models.BooleanField()
    #availableBalance (Money) [bank]
    #availableCash (Money) [creditCard]
    #availableCredit(Money) [creditCard, loan]
    #availableLoan (Money) [investment]
    #accountBalance (Money) [bank, creditCard, investment, insurance, loan, bill]
    #cash (Money) [investment]
    #cashValue (Money) [insurance]
    classification = models.CharField(max_length=14, blank=True)#E [bank, creditCard, investment]
    container = models.CharField(max_length=25)
    #currentBalance (Money) [bank]
    dueDate = models.DateField(blank=True) #[bill, creditCard, insurance, loan]
    expirationDate = models.DateField(blank=True) #[insurance]
    #faceAmount (Money) #[insurance]
    interestRate = models.FloatField(blank=True) #[bank, loan]
    #lastPayment (Money) [bill]
    #accountLastPaymentAmount (Money) [creditCard, insurance, bill, loan]
    lastPaymentDate = models.DateField(blank=True)
    lastUpdated = models.DateTimeField(blank=True)
    isManual = models.BooleanField()
    #marginBalance (Money) [investment]
    #maturityAmount (Money) [bank]
    maturityDate = models.DateField(blank=True)# [bank, loan]
    #minimumAmountDue (Money) [creditCard, insurance, bill, loan]
    #moneyMarketBalance (Money) [investment]
    nickname = models.CharField(max_length=40, blank=True)
    #accountRefreshInfo (RefreshInfo)
    #runningBalance (Money) [creditCard]
    status = models.CharField(max_length=12, blank=True) #E
    #totalCashLimit (Money) [creditCard]
    #totalCreditLine (Money) [creditCard]
    #totalUnvestedBalance (Money) [investment]
    #totalVestedBalance (Money) [investment]
    accountType = models.CharField(max_length=40, blank=True)#[investment, insurance, bill, loan, bank, creditCard]
    #escrowBalance (Money) [loan]
    homeInsuranceType = models.CharField(max_length=30, blank=True)#E (But undocumented?) [insurance]
    interestRate = models.FloatField(blank=True)# [bank]
    lifeInsuranceType = models.CharField(max_length=30, blank=True)#E (But undocumented?) [insurance]
    #originalLoanAmount(Money) [loan]
    providerId = models.PositiveIntegerField(blank=True)
    providerName = models.CharField(max_length=40, blank=True)
    #principalBalance (Money) [loan]
    policyStatus = models.CharField(max_length=30, blank=True)#E (But undocumented?) [insurance]
    premiumPaymentTerm = models.PositiveIntegerField(blank=True)# [insurance]
    #recurringPayment (Money) [loan]
    term = models.TextField(blank=True)# [bank, loan]
    ## NOTE: No idea on how the above is structured.
    ## will revamp when I have an actual example. We
    ## will just accept the string for now.
    #totalCreditLimit (Money) [loan]
    enrollmentDate = models.DateField(blank=True)#[reward]
    primaryRewardUnit = models.CharField(max_length=25, blank=True)#[reward]
    #rewardBalance (RewardBalance) [reward]
    currentLevel = models.CharField(max_length=20, blank=True)#[reward]
    nextLevel = models.CharField(max_length=20, blank=True)#[reward]
    #shortBalance (Money) [investment]
    #holderProfile (I'm going to leave this one out, since 
    #I feel its purpose is fulfilled by the UserData/UserProfile)
    #lastEmployeeContributionAmount (Money) [investment]
    lastEmployeeContributionDate = models.DateField(blank=True) #[investment]
    providerAccountId = models.BigIntegerField(blank=True) #[bank, creditCard, insurance, loan, bill, investment]

### YODLEE TRANSACTIONS

class Transaction(models.Model):
    _id = models.BigIntegerField()
    accountID = models.BigIntegerField()
    #transactionAmount (Money)
    baseType = models.CharField(max_length=7, blank=True)#E
    category = models.CharField(max_length=20, blank=True)
    container = models.CharField(max_length=20, blank=True)
    cusipNumber = models.CharField(max_length=9, blank=True)#[investment]
    date = models.DateField()
    #description (Description) [bank, creditCard, insurance, loan, bill, investment]
    ##NOTE The documentation says they have two description
    ## fields for a transaction, one is just a string, and
    ## the other is a composite of strings. This is dumb
    ## and I know it but we'll change as we see more objects
    ## come in. 
    holdingDescription = models.TextField(blank=True)#[investment]
    #interest (Money) [loan]
    isManual = models.BooleanField()
    memo = models.TextField(blank=True)
    #merchant [bank, CreditCard, insurance, loan, bill, investment]
    ##NOTE This will be similar to the loginfield in that
    ## it's based on the presented form in the example,
    ## I have a feeling that this will be different for
    ## each vendor, but we'll worry about that when we get
    ## to it.
    postDate = models.DateField(blank=True)#[bank, creditCard, insurance, loan]
    postingOrder = models.PositiveIntegerField(blank=True)
    #transactionPrice (Money) [investment]
    principal = models.PositiveIntegerField(blank=True) #[loan]
    quantity = models.PositiveIntegerField(blank=True) #[investment]
    settleDate = models.DateField(blank=True) #[investment]
    transactionStatus = models.CharField(max_length=11, blank=True)#E
    symbol = models.CharField(max_length=5, blank=True) #[investment]
    transactionDate = models.DateField()
    _type = models.CharField(max_length=40, blank=True)#E

### YODLEE TRANSACTIONCATEGORY

class TransactionCategory(models.Model):
    _id = models.BigIntegerField()
    name = models.CharField(max_length=40)
    _type = models.CharField(max_length=21)#E
    isBudgetable = models.BooleanField()
    isDeleted = models.BooleanField()
    isSmallBusinessCategory = models.BooleanField()
    source = models.CharField(max_length=10, blank=True)

### YODLEE HOLDINGS

class Holding(models.Model):
    userData = models.ForeignKey(
        UserData,
        on_delete=models.CASCADE,
        )

    accountId = models.BigIntegerField()
    #costBasis (Money)
    cusipNumber = models.CharField(max_length=9, blank=True)
    description = models.CharField(max_length=30, blank=True)
    holdingType = models.CharField(max_length=20, blank=True)
    #holdingPrice (Money)
    quantity = models.PositiveIntegerField(blank=True)
    symbol = models.CharField(max_length=5, blank=True)
    unvestedQuantity = models.PositiveIntegerField(blank=True)#[EMPLOYEE_STOCK_OPTION]
    #unvestedValue (Money) [EMPLOYEE_STOCK_OPTION]
    #value (Money) [EMPLOYEE_STOCK_OPTION]
    vestedQuantity = models.PositiveIntegerField(blank=True)#[EMPLOYEE_STOCK_OPTION]
    vestedSharesExercisable = models.PositiveIntegerField(blank=True)#[EMPLOYEE_STOCK_OPTION]
    #vestedValue (Money) [EMPLOYEE_STOCK_OPTION]
    vestingDate = models.DateField(blank=True) #[EMPLOYEE_STOCK_OPTION]
    contractQuanitty = models.PositiveIntegerField(blank=True) #[Commodity]
    couponRate = models.FloatField(blank=True) #[Bond]
    currencyType = models.CharField(max_length=3, blank=True)
    #employeeContribution (Money) [Employee_Stock_Option]
    #employerContribution (Money) [Employee_Stock_Option]
    exercisedQuantity = models.PositiveIntegerField(blank=True)#[Employee_Stock_Option]
    expirationDate = models.DateField(blank=True)#[Option, Future, Commodity]
    grantDate = models.DateField(blank=True)#[Employee_Stock_Option]
    interestRate = models.FloatField(blank=True)#[CD]
    maturityDate = models.DateField(blank=True)#[CD, Bond]
    optionType = models.CharField(max_length=4, blank=True)#E, call or put [Option]
    #parValue (Money) [Bond]
    #spread (Money) [Employee_Stock_Option]
    #strikePrice (Money) [Employee_Stock_Option]
    term = models.TextField(blank=True)#[CD]
    ##NOTE: I believe that the term field handles a time delta
    ## not yet sure if it contains the end or whatever. We can
    ## probably use a django duration field to store it. Will
    ## currently just store the raw string until I can fix it.
    providerAccountID = models.BigIntegerField(blank=True)#[bank, creditCard, insurance, loan, bill, investment]


    def __str__(self):
        return "%s" % (self.holdingType)

### YODLEE ASSETCLASSIFICATION

class AssetClassification(models.Model):
    classificationType = models.CharField(max_length=10)#E (assetClass, country, sector, style)
    classificationValue = models.CharField(max_length=30)#E
    allocation = models.FloatField()

### YODLEE HISTORICALBALANCES

class HistoricalBalance(models.Model):
    date = models.DateField()
    asOfDate = models.DateField()
    #balance (Money)
    isAsset = models.BooleanField()

### YODLEE INVESTMENTPLAN

class InvestmentPlan(models.Model):
    planId = models.BigIntegerField()
    name = models.CharField(max_length=40, blank=True)
    number = models.BigIntegerField(blank=True)
    provider = models.CharField(max_length=40, blank=True)
    asOfDate = models.DateField()
    returnAsOfDate = models.DateField()
    feesAsOfDate = models.DateField()

### YODLEE INVESTMENTOPTION

class InvestmentOption(models.Model):
    optionId = models.BigIntegerField()
    cusipNumber = models.CharField(max_length=9, blank=True)
    description = models.CharField(max_length=40, blank=True)
    fiveYearReturn = models.FloatField(blank=True)
    holdingType = models.CharField(max_length=20, blank=True)
    isin = models.CharField(max_length=12, blank=True)
    oneMonthReturn = models.FloatField(blank=True)
    oneYearReturn = models.FloatField(blank=True)
    #optionPrice (Money)
    priceAsOfDate = models.DateField()
    sedol = models.CharField(max_length=7, blank=True)
    symbol = models.CharField(max_length=5, blank=True)
    tenYearReturn = models.FloatField(blank=True)
    threeMonthReturn = models.FloatField(blank=True)
    inceptionToDateReturn = models.FloatField(blank=True)
    yearToDateReturn = models.FloatField(blank=True)
    inceptionDate = models.DateField(blank=True)
    grossExpenseRatio = models.FloatField(blank=True)
    #grossExpenseAmount (Money)
    netExpenseRatio = models.FloatField(blank=True)
    #netExpenseAmount (Money)
    ## NOTE: In the examples, all the returns are kept
    ## in a 'historicReturns' object. If that's the case
    ## in actual practice, I'll change it. Till then, I'll
    ## keep in place with what's documented.

### YODLEE STATEMENTS

class Statement(models.Model):
    account = models.CharField(max_length=20)
    _id = models.BigIntegerField(blank=True) # [credit, bill, loan, insurance]
    statementDate = models.DateField()
    billingPeriodStart = models.DateField()
    billingPeriodEnd = models.DateField()
    dueDate = models.DateField()
    #amountDue (Money)
    #lastPaymentAmount (Money)
    lastPaymentDate = models.DateField()
    isLatest = models.BooleanField()
    lastUpdated = models.DateTimeField()
    #minimumPayment (Money) [creditCard, loan]
    #newCharges (Money) [creditCard, loan]
    apr = models.FloatField(blank=True) #[creditCard]
    cashApr = models.FloatField(blank=True) #[creditCard]
    #interestAmount (Money) [loan]
    #principalAmount (Money) [loan]
    #loanBalance (Money) [loan]

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
    statusMessage = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=40, blank=True)
    #Also, the statuses can be really longwinded.
    additionalStatus = models.CharField(max_length=40, blank=True)
    nextRefreshScheduled = models.DateTimeField()
    lastRefreshed = models.DateTimeField()
    lastRefreshAttempt = models.DateTimeField()
    actionRequested = models.CharField(max_length=20, blank=True)
    #Action Requested will read 'UPDATE_CREDENTIALS'
    #if the provider account needs an action to be taken
    #due to erros. This field is not available in the
    #response for refresh and provider endpoint APIs
    message = models.TextField(blank=True)

class RewardBalance(models.Model):
    description = models.TextField(blank=True)
    balance = models.PositiveIntegerField()
    units = models.CharField(max_length=30, blank=True)
    balanceType = models.CharField(max_length=20, blank=True)#E
    expiryDate = models.DateField()
    balanceToLevel = models.PositiveIntegerField(blank=True)
    balanceToReward = models.PositiveIntegerField(blank=True)


### YODLEE PROVIDER

class ContainerName(models.Model):
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE
        )
    name = models.CharField(max_length=10)

class LoginForm(models.Model):
    provider = models.OneToOneField(
        Provider,
        on_delete=models.CASCADE
        )
    _id = models.PositiveIntegerField()
    forgetPasswordURL = models.URLField(blank=True)
    formType = models.CharField(max_length=20, blank=True)
    #row

## LoginForm models
class Row(models.Model):
    loginForm = models.ForeignKey(
        LoginForm,
        on_delete=models.CASCADE,
        )
    _id = models.PositiveIntegerField()
    label = models.CharField(max_length=20, blank=True)
    # Might swap out the form and fieldrow for 
    # positive integers, but the way they were
    # formatted looked like chars might be the 
    # better choice. Will revamp upon seeing actual
    # results.
    form = models.CharField(max_length=4, blank=True)
    fieldRowChoice=models.CharField(max_length=4, blank=True)
    #field

# Row models

class Field(models.Model):
    _id = models.PositiveIntegerField()
    name = models.CharField(max_length=20, blank=True)
    _type = models.CharField(max_length = 20, blank=True)
    value = models.TextField(blank=True)
    isOptional = models.BooleanField()
    valueEditable = models.BooleanField()

### YODLEE PROVIDERACCOUNTS
class ProviderRefreshInfo(RefreshInfo):
    providerAccounts = models.OneToOneField(
        ProviderAccounts,
        on_delete=models.CASCADE,
        )


### YODLEE ACCOUNTS
class _401kloan(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class accountAmountDue(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class annuityBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class availableBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class availableCash(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class availableCredit(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class availableLoan(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class accountBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class cash(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class cashValue(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class currentBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class faceAmount(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class lastPayment(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class accountLastPaymentAmount(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class marginBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class matuityAmount(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class minimumAmountDue(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class moneyMarketBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class accountRefreshInfo(RefreshInfo):
    account = models.OneToOneField(
        Account,
        on_delete=models.CASCADE,
        )

class runningBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class totalCashLimit(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class totalCreditLine(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class totalUnvestedBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class totalVestedBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class escrowBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class originalLoanAmount(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class principalBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class recurringPayment(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class totalCreditLimit(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class accountRewardBalance(RewardBalance):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class shortBalance(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

class lastEmployeeContributionAmount(Money):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        )

### YODLEE TRANSACTIONS

class transactionAmount(Money):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        )

class description(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        )
    simple = models.TextField()
    consumer = models.TextField()
    original = models.TextField()

class interest(Money):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        )

class merchant(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        )
    name = models.CharField(max_length=30)
    #coordinates
    #address

class transactionPrice(Money):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        )

### YODLEE HOLDINGS

class costBasis(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class holdingPrice(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class unvestedValue(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class value(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class vestedValue(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class employeeContribution(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class employerContribution(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class parValue(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class spread(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

class strikePrice(Money):
    holding = models.OneToOneField(
        Holding,
        on_delete=models.CASCADE,
        )

### YODLEE HISTORICALBALANCES

class balance(Money):
    historicalBalance = models.OneToOneField(
        HistoricalBalance,
        on_delete=models.CASCADE,
        )

### YODLEE INVESTMENTOPTION

class optionPrice(Money):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        )

class grossExpenseAmount(Money):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        )

class netExpenseAmount(Money):
    investmentOption = models.OneToOneField(
        InvestmentOption,
        on_delete=models.CASCADE,
        )

### YODLEE STATEMENTS

class amountDue(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

class lastPaymentAmount(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

class minimumPayment(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

class newCharges(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

class interestAmount(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

class principalAmount(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

class loanBalance(Money):
    statement = models.OneToOneField(
        Statement,
        on_delete=models.CASCADE,
        )

### ACCESSORY MODELS (MODELS FOR CONVENIENCE)

class Coordinates(models.Model):
    merchant = models.ForeignKey(
        merchant,
        on_delete=models.CASCADE,
        )
    latitude = models.FloatField()
    longitude = models.FloatField()

class Address(models.Model):
    merchant = models.ForeignKey(
        merchant,
        on_delete=models.CASCADE,
        )
    city = models.CharField(max_length=40)
    state = models.CharField(max_length=2, blank=True)
    country = models.CharField(max_length=5)
    _zip = models.CharField(max_length=5, blank=True)

class Stock(models.Model):
    symbol = models.CharField(max_length=5, primary_key=True)
    lastUpdated = models.DateField()

    def __str__(self):
        return self.symbol

class StockPrice(models.Model):
    stock = models.ForeignKey(
        Stock,
        on_delete=models.CASCADE,
        )
    date = models.DateField()
    price = models.DecimalField(max_digits=11, decimal_places=6)

    def __str__(self):
        return "%s %s" % (self.stock.symbol, str(self.date))