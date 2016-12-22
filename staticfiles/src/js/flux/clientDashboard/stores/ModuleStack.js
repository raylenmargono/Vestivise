/**
 * Created by raylenmargono on 12/10/16.
 */

class ModuleStack{
    constructor(type){
        this.index = -1;
        this.modules = [];
        this.moduleMap = {};
        this.type = type;
    }

    getList(){
        return this.modules;
    }

    getType(){
        return this.type;
    }

    getCurrentModule(){
        if(this.index == -1){
            return null;
        }
        return this.modules[this.index];
    }

    pushModule(module){
        this.modules.push(module);
        if(this.index == -1){
            this.index = 0;
        }
        this.moduleMap[module.getName()] = module;
    }

    updateData(module, data){
        const moduleObj = this.moduleMap[module.getName()];
        moduleObj.setData(data);
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