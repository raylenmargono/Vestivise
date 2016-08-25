class Module{

    constructor(moduleName, account, isAddOn, endpoint, moduleID){
        this.moduleName = moduleName;
        this.account = account;
        this.isAddOn = isAddOn;
        this.endpoint = endpoint;
        this.moduleID = moduleID;
    }

    getName(){
        return this.moduleName;
    }

    getModuleID(){
        return this.moduleID;
    }

    getAccount(){
        return this.account;
    }

    getChartJSON(){

    }

    getChartCSS(){

    }

    isAddOn(){
        return this.isAddOn;
    }

    getEndPoint(){
        return this.endpoint;
    }

}

export default Module;