var initialData = {};

const returnData = {
	"returns" : [0.3, 2, 4, 5],
    "benchMark" : [0.48,4.06,4.70,8.94]
}

const assetData = {
	assets :[
		{
			name : "Bonds",
			percentage : 35,
		},
		{
			name : "Stocks",
			percentage : 26.8,
		},
		{
			name: 'Commodities',
			percentage: 28.8,
		},
		{
			name : 'Real Estate',
			percentage: 10,
		}
	],
	totalAssets : 30000 
}

initialData.account_modules = [
	{
		module : {
			data : returnData,
			moduleName : "Basic Return",
			isAddOn : false,
			endpoint : "basicReturns",
			account : "",
			category : "Return",
			moduleID : 'basicReturns'
		}
	},
	{
		module : {
			data : assetData,
			moduleName : "Basic Asset",
			isAddOn : false,
			endpoint: "basicAsset",
			account : "basicAsset",
			category : "Asset",
			moduleID : 'basicAsset'
		}
	},
	{
		module : {
			data : {
				riskLevel : "moderate"
			},
			moduleName : "Basic Risk",
			isAddOn : false,
			endpoint: "basicRisk",
			account : "basicRisk",
			category : "Risk",
			moduleID : 'basicRisk'
		}
	},
	{
		module : {
			data : {
				fee : 2.2,
				averagePlacement : "greater"
			},
			moduleName : "Basic Fee",
			isAddOn : false,
			endpoint: "basicCost",
			account : "",
			category : "Cost",
			moduleID : 'basicCost'
		}
	}
];

initialData.linkedAccount = true;
initialData.processing = false;


export default initialData;