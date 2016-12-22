/**
 * Created by raylenmargono on 12/10/16.
 */
class Module{
    constructor(name,endpoint, category){
        this.name = name;
        this.endpoint = endpoint;
        this.category = category;
        this.data = null;
    }

    getData(){
        return this.data;
    }

    setData(data){
        this.data = data["data"];
    }

    getEndpoint(){
        return this.endpoint;
    }

    getCategory(){
        return this.category;
    }

    getName(){
        return this.name;
    }

    getData(){
        return this.data;
    }
}

export default Module;