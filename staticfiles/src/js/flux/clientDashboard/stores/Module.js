/**
 * Created by raylenmargono on 12/10/16.
 */


class Module{
    constructor(name, endpoint, category, mID){
        this.name = name;
        this.endpoint = endpoint;
        this.category = category;
        this.data = null;
        this.mID = mID;
        this.timeOnScreen = 0;
        setInterval(function(){
            if($('#' + this.mID).length != 0 && $('#' + this.mID).visible( true )){
                this.timeOnScreen += 1;
            }
        }.bind(this), 1000);
    }

    getID(){
        return this.mID;
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