import Module from "./module";

class Stack{

	constructor(){
		this.index = -1;
		this.modules = [];
	}

    getCurrentModule(){
        if(this.index == -1){
            return null;
        }
        return this.modules[this.index];
    }

	pushModule(module){
        const name = module.name;
        const category = module.category;
        const endpoint = module.endpoint;
        const moduleID = module.moduleID;

        const m = new Module(name, category, endpoint, moduleID);
		this.modules.push(m);
		if(this.index == -1){
			this.index = 0;
		}
	}

	next(){
		if(this.index++ == this.modules.length){
			this.index = 0;
		}
	}

}

export default Stack;