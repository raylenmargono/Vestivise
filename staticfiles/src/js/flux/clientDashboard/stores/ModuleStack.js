/**
 * Created by raylenmargono on 12/10/16.
 */

class ModuleStack{
    constructor(type){
        this.index = -1;
        this.modules = [];
        this.moduleMap = {};
        this.type = type;
        this.pendingData = 0;
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