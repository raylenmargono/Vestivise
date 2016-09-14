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

holdingsTestData = {
  "holding": [
    {
        "id": 1840,
        "costBasis": None,
        "holdingPrice": {
            "id": 6935,
            "amount": 47.7788,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6936,
            "amount": 217567.1,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10268227,
        "cusipNumber": '92202E888',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "Target 2030 Trust Select",
        "holdingType": "mutualFund",
        "quantity": 4553.63,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10135595,
        "yodleeAccount": 45
    },
    {
        "id": 1841,
        "costBasis": None,
        "holdingPrice": {
            "id": 6937,
            "amount": 10.7596,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6938,
            "amount": 4763.08,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '693394538',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "PIMCO VIT Total Return Portfolio - Advisor Class",
        "holdingType": "mutualFund",
        "quantity": 442.6831,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1842,
        "costBasis": None,
        "holdingPrice": {
            "id": 6939,
            "amount": 9.7291,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6940,
            "amount": 2926.48,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '649280849',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "American Funds IS New World - Class 4",
        "holdingType": "mutualFund",
        "quantity": 300.7981,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1843,
        "costBasis": None,
        "holdingPrice": {
            "id": 6941,
            "amount": 11.5062,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6942,
            "amount": 4784.75,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": "693391245",
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "PIMCO VIT Foreign Bond Portfolio (U.S. Dollar-Hedged) - Advisor Class",
        "holdingType": "mutualFund",
        "quantity": 415.8411,
        "symbol": "PFOAX",
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1844,
        "costBasis": None,
        "holdingPrice": {
            "id": 6943,
            "amount": 8.7962,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6944,
            "amount": 7539.98,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '56064B423',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "MainStay VP Absolute Return Multi-Strategy - Service Class",
        "holdingType": "mutualFund",
        "quantity": 857.1899,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1845,
        "costBasis": None,
        "holdingPrice": {
            "id": 6945,
            "amount": 12.2348,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6946,
            "amount": 9611.24,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '56062F657',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "Mainstay VP Unconstrained Bond Portfolio - Service Class",
        "holdingType": "mutualFund",
        "quantity": 785.5647,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1846,
        "costBasis": None,
        "holdingPrice": {
            "id": 6947,
            "amount": 9.8899,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6948,
            "amount": 3871.69,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": "008892655",
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "Invesco V.I. International Growth Fund - Series II",
        "holdingType": "mutualFund",
        "quantity": 391.4788,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1847,
        "costBasis": None,
        "holdingPrice": {
            "id": 6949,
            "amount": 19.6278,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6950,
            "amount": 33899.82,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '56063U794',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "MainStay VP Growth Allocation Portfolio - Service Class",
        "holdingType": "mutualFund",
        "quantity": 1727.1342,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1848,
        "costBasis": None,
        "holdingPrice": {
            "id": 6951,
            "amount": 24.3493,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6952,
            "amount": 2906.51,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '641222856',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "Neuberger Berman AMT MidCap Growth Portfolio - Class S",
        "holdingType": "mutualFund",
        "quantity": 119.3673,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1849,
        "costBasis": None,
        "holdingPrice": {
            "id": 6953,
            "amount": 22.2935,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6954,
            "amount": 4816.27,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": "55273F779",
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "MFS Investors Trust Series - Service Class",
        "holdingType": "mutualFund",
        "quantity": 216.0393,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1850,
        "costBasis": None,
        "holdingPrice": {
            "id": 6955,
            "amount": 23.5537,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6956,
            "amount": 11626.18,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '92914K602',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "Fidelity  VIP Contrafund  - Service Class 2",
        "holdingType": "mutualFund",
        "quantity": 493.6028,
        "symbol": "FAVCF",
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    {
        "id": 1851,
        "costBasis": None,
        "holdingPrice": {
            "id": 6957,
            "amount": 17.7869,
            "currency": "USD"
        },
        "unvestedValue": None,
        "value": {
            "id": 6958,
            "amount": 9641.52,
            "currency": "USD"
        },
        "vestedValue": None,
        "employeeContribution": None,
        "employerContribution": None,
        "parValue": None,
        "spread": None,
        "strikePrice": None,
        "assetClassifications": [],
        "accountID": 10265012,
        "cusipNumber": '56062F772',
        "createdAt": "2016-08-23T12:59:50.732830Z",
        "description": "MainStay VP High Yield Corporate Bond - Service Class",
        "holdingType": "mutualFund",
        "quantity": 542.0564,
        "symbol": None,
        "unvestedQuantity": None,
        "vestedQuantity": None,
        "vestedSharesExercisable": None,
        "vestingDate": None,
        "contractQuantity": None,
        "couponRate": None,
        "currencyType": None,
        "exercisedQuantity": None,
        "expirationDate": None,
        "grantDate": None,
        "interestRate": None,
        "maturityDate": None,
        "optionType": "unknown",
        "term": None,
        "providerAccountID": 10134485,
        "yodleeAccount": 45
    },
    # {
    #     "id": 1852,
    #     "costBasis": None,
    #     "holdingPrice": None,
    #     "unvestedValue": None,
    #     "value": {
    #         "id": 6959,
    #         "amount": 69320.1,
    #         "currency": "USD"
    #     },
    #     "vestedValue": None,
    #     "employeeContribution": None,
    #     "employerContribution": None,
    #     "parValue": None,
    #     "spread": None,
    #     "strikePrice": None,
    #     "assetClassifications": [],
    #     "accountID": 10265012,
    #     "cusipNumber": None,
    #     "createdAt": "2016-08-23T12:59:50.732830Z",
    #     "description": "6-Month Dollar Cost Averaging Advantage",
    #     "holdingType": "stock",
    #     "quantity": None,
    #     "symbol": None,
    #     "unvestedQuantity": None,
    #     "vestedQuantity": None,
    #     "vestedSharesExercisable": None,
    #     "vestingDate": None,
    #     "contractQuantity": None,
    #     "couponRate": None,
    #     "currencyType": None,
    #     "exercisedQuantity": None,
    #     "expirationDate": None,
    #     "grantDate": None,
    #     "interestRate": None,
    #     "maturityDate": None,
    #     "optionType": "unknown",
    #     "term": None,
    #     "providerAccountID": 10134485,
    #     "yodleeAccount": 45
    # }
]
}

holdings_sequel = {
  "stock":{
  "holding": [
     {
        "id": 5555,
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
