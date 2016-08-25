import { ModuleConst } from '../const/module.const';
import BasicRiskModule from '../modules/basic/basicRiskModule.jsx';
import BasicFeeModule from '../modules/basic/basicFeeModule.jsx';
import BasicAssetModule from '../modules/basic/basicAssetModule.jsx';
import BasicReturnModule from '../modules/basic/basicReturnModule.jsx';

import React from 'react';

export default class ModuleFactory{
	static createModule(moduleName, endpoint){
		var module;
		switch(moduleName){
			case ModuleConst.BASIC_RISK:
				module = (<BasicRiskModule endpoint={endpoint}/>);
				break;
			case ModuleConst.BASIC_RETURN:
				module = (<BasicReturnModule endpoint={endpoint}/>);
				break;
			case ModuleConst.BASIC_ASSET:
				module = (<BasicAssetModule endpoint={endpoint}/>);
				break;
			case ModuleConst.BASIC_FEE:
				module = (<BasicFeeModule endpoint={endpoint}/>);
				break;
		}

		return module;
	}
}