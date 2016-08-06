yodlee_account_response = {
        "account": [
           {
              "CONTAINER": "bank",
              "providerAccountId": 12345,
              "accountName": "SMB account",
              "id": 801503,
              "accountNumber": "xxxx4933",
              "availableBalance": {
                 "amount": 4699,
                 "currency": "USD"
              },
              "accountType": "SAVINGS",
              "isAsset": "true",
              "balance": {
                 "amount": 84699,
                 "currency": "USD"
              },
              "providerId": 16441,
              "providerName": "Dag Site",
              "refreshinfo": {
                 "statusCode": 0,
                 "statusMessage": "OK",
                 "lastRefreshed": "2015-09-20T14:46:23Z",
                 "lastRefreshAttempt": "2015-09-20T14:46:23Z",
                 "nextRefreshScheduled": "2015-09-23T14:46:23Z"
              }, 
              "accountStatus": "ACTIVE"
           }
        ]
    }

yodlee_account_response_update = {
        "account": [
           {
              "CONTAINER": "bank",
              "providerAccountId": 12345,
              "accountName": "SMB account",
              "id": 801503,
              "accountNumber": "xxxx4933",
              "availableBalance": {
                 "amount": 1,
                 "currency": "USD"
              },
              "accountType": "SAVINGS",
              "isAsset": "true",
              "balance": {
                 "amount": 1,
                 "currency": "USD"
              },
              "providerId": 16441,
              "providerName": "Dag Site",
              "refreshinfo": {
                 "statusCode": 0,
                 "statusMessage": "OK",
                 "lastRefreshed": "2015-09-20T14:46:23Z",
                 "lastRefreshAttempt": "2015-09-20T14:46:23Z",
                 "nextRefreshScheduled": "2015-09-23T14:46:23Z"
              }, 
              "accountStatus": "ACTIVE"
           }
        ]
    }


yodlee_account_response_multiple = {
  "account": [
    {
      "CONTAINER": "bank",
      "providerAccountId": 10120525,
      "isManual": "false",
      "accountName": "TESTDATA1",
      "accountStatus": "ACTIVE",
      "accountNumber": "xxxx3xxx",
      "isAsset": "true",
      "balance": {
        "amount": 9044.78,
        "currency": "USD"
      },
      "id": 10227542,
      "lastUpdated": "2016-08-03T00:25:34Z",
      "providerId": "16441",
      "providerName": "Dag Site",
      "availableBalance": {
        "amount": 65454.78,
        "currency": "USD"
      },
      "currentBalance": {
        "amount": 9044.78,
        "currency": "USD"
      },
      "accountType": "SAVINGS",
      "holderProfile": [
        {
          "name": {
            "displayed": "accountHolder"
          }
        }
      ],
      "refreshinfo": {
        "statusCode": 0,
        "statusMessage": "OK",
        "lastRefreshed": "2016-08-03T00:25:34Z",
        "lastRefreshAttempt": "2016-08-03T00:25:34Z",
        "nextRefreshScheduled": "2016-08-04T09:48:06Z"
      }
    },
    {
      "CONTAINER": "bank",
      "providerAccountId": 10120525,
      "isManual": "false",
      "accountName": "TESTDATA",
      "accountStatus": "ACTIVE",
      "accountNumber": "xxxx3xxx",
      "isAsset": "true",
      "balance": {
        "amount": 44.78,
        "currency": "USD"
      },
      "id": 10227541,
      "lastUpdated": "2016-08-03T00:25:34Z",
      "providerId": "16441",
      "providerName": "Dag Site",
      "availableBalance": {
        "amount": 54.78,
        "currency": "USD"
      },
      "currentBalance": {
        "amount": 44.78,
        "currency": "USD"
      },
      "accountType": "CHECKING",
      "holderProfile": [
        {
          "name": {
            "displayed": "accountHolder"
          }
        }
      ],
      "refreshinfo": {
        "statusCode": 0,
        "statusMessage": "OK",
        "lastRefreshed": "2016-08-03T00:25:34Z",
        "lastRefreshAttempt": "2016-08-03T00:25:34Z",
        "nextRefreshScheduled": "2016-08-04T09:48:06Z"
      }
    },
    {
      "CONTAINER": "creditCard",
      "providerAccountId": 10120525,
      "isManual": "false",
      "accountName": "CREDIT CARD",
      "accountStatus": "ACTIVE",
      "accountNumber": "xxxx8614",
      "isAsset": "false",
      "balance": {
        "amount": 1636.44,
        "currency": "USD"
      },
      "id": 10224034,
      "lastUpdated": "2016-08-03T00:25:33Z",
      "providerId": "16441",
      "providerName": "Dag Site",
      "accountType": "UNKNOWN_1",
      "availableCash": {
        "amount": 600,
        "currency": "USD"
      },
      "availableCredit": {
        "amount": 1363,
        "currency": "USD"
      },
      "totalCashLimit": {
        "amount": 600,
        "currency": "USD"
      },
      "totalCreditLine": {
        "amount": 3000,
        "currency": "USD"
      },
      "refreshinfo": {
        "statusCode": 0,
        "statusMessage": "OK",
        "lastRefreshed": "2016-08-03T00:25:33Z",
        "lastRefreshAttempt": "2016-08-03T00:25:33Z",
        "nextRefreshScheduled": "2016-08-04T11:30:36Z"
      }
    }
  ]
}


holding_types = {
  "holdingType": [
    "CD",
    "ETF",
    "bond",
    "commodity",
    "currency",
    "employeeStockOption",
    "future",
    "insuranceAnnuity",
    "moneyMarketFund",
    "mutualFund",
    "option",
    "other",
    "preferredStock",
    "remic",
    "stock",
    "unitInvestmentTrust",
    "unknown",
    "warrants"
  ]

}

holdings = {
  "holding": [
     {
        "id": 1347615,
        "accountId": 1111496500,
        "providerAccountId": 12345,
        "costBasis": {
          "amount":2500,
          "currency": "USD"
        },
        "cusipNumber":999999999,
        "description": "IBM stocks",
        "holdingType":"stock",
        "price": {
          "amount":2500,
          "currency": "USD"
        },
        "quantity":200,
        "symbol":"IBM",
        "value": {
          "amount":500000,
          "currency": "USD"
        },
        "assetClassification": [{
           "classificationType": "Style",
          "classificationValue": "Low Risk Low Reward",
          "allocation": 100
        }, {
          "classificationType": "Country",
          "classificationValue": "US",
          "allocation": 100
        }]
     }
  ]
}

investment_options={
"account": [
     {
        "id": 1111498734,
        "investmentPlan": {
             "lastUpdated": "2015-09-25T09:46:38Z",
             "providerId": 16441,
             "providerName": "Dag Site",
             "asOfDate": "2015-01-14",
             "planName": "wealthYSL2",
             "planNumber": 3040,
             "id": 10005617,
             "returnAsOfDate": '2015-11-14',
             "feesAsOfDate": '2015-11-14',
           }, 
        "investmentOption": [
           {
             "holdingType": "mutualFund",
             "cusipNumber": "00078H240",
             "description": 'YSL',
             "isin": 'US00078H2408',
             "id": 10006073,
             "price": {
               "amount": 24.9496,
               "currency": "USD"
             },
             "inceptionDate": '2015-11-14',
             "inceptionToDateReturn": 16.11,
             "yearToDateReturn": 6.31,
             "grossExpenseRatio": 0.11,
             "netExpenseRatio": 0.11,
             "grossExpenseAmount": {
               "amount": 12.88,
               "currency": "USD"
             },
             "netExpenseAmount": {
               "amount": 12.88,
               "currency": "USD"
             },
             "sedol": 'B8DLKR2',
             "symbol": 'AVEIX',
             "historicReturns": {
               "oneMonthReturn": 10,
               "threeMonthReturn": 7,
               "oneYearReturn": 13,
               "threeYearReturn": 14.5,
               "fiveYearReturn": 10.7,
               "tenYearReturn": 20
             } 
           } 
        ] 
     } 
  ]
  }