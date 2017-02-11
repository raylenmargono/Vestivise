/**
 * Created by raylenmargono on 12/10/16.
 */
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';
import ModuleGroup from 'jsx/apps/clientDashboard/dashboard/const/moduleGroup.jsx';

class ModuleStack{
    constructor(type){
        this.index = -1;
        this.moduleMap = {};
        this.type = type;
        this.pendingData = 0;
    }

    getList(){
        switch(this.type){
            case ModuleGroup.ASSET:
                return[
                    this.moduleMap[ModuleType.HOLDING_TYPE],
                    this.moduleMap[ModuleType.STOCK_TYPE],
                    this.moduleMap[ModuleType.BOND_TYPE]
                ];
            case ModuleGroup.RETURN:
                return[
                    this.moduleMap[ModuleType.RETURNS],
                    this.moduleMap[ModuleType.CONTRIBUTION_WITHDRAW],
                    this.moduleMap[ModuleType.RETURNS_COMPARE],
                ];
            case ModuleGroup.RISK:
                return[
                    this.moduleMap[ModuleType.RISK_PROFILE],
                    this.moduleMap[ModuleType.RISK_AGE_PROFILE]
                ];
            case ModuleGroup.COST:
                return[
                    this.moduleMap[ModuleType.FEES],
                    this.moduleMap[ModuleType.COMPOUND_INTEREST],
                ];
            case ModuleGroup.OTHER:
                return[
                    this.moduleMap[ModuleType.PORT_HOLD],
                ];
        }
    }

    getType(){
        return this.type;
    }

    pushModule(module){
        if(this.index == -1){
            this.index = 0;
        }
        this.moduleMap[module.getName()] = module;
        this.pendingData += 1;
    }

    updateData(module, data){
        const moduleObj = this.moduleMap[module.getName()];
        moduleObj.setData(data);
        this.pendingData -= 1;
    }

    next(){
        if(++this.index == this.modules.length){
			this.index = 0;
		}
    }

    prev(){
        if(--this.index < 0){
			this.index = this.modules.length - 1;
		}
    }

}

export default ModuleStack;