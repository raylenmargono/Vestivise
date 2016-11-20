class Module{

    constructor(name, category, endpoint, moduleID){
        this.name = name;
        this.category = category;
        this.endpoint = endpoint;
        this.moduleID = moduleID;
    }

    getName(){
        return this.name;
    }

    getModuleID(){
        return this.moduleID;
    }

    getCategory(){
        return this.category;
    }

    getEndPoint(){
        return this.endpoint;
    }

}

export default Module;