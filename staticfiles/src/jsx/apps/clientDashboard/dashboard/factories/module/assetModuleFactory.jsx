import React, {Component} from 'react';
import VestiBlock from 'jsx/apps/clientDashboard/dashboard/modules/vestiBlock.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';


class AssetModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    constructHoldingType(data){
        const percentages = data['percentages'];
        var groups = {};
        for(var key in percentages){
            var group = key.replace("Short", "").replace("Long", "");
            if(!groups[group]){
                groups[group] = {
                    "total" : 0,
                    "subgroup" : []
                };
            }
            groups[group]["total"] += percentages[key];
            groups[group]["subgroup"].push({
                "title" : key.replace("Short", " Short").replace("Long", " Long"),
                "percentage" : percentages[key],
                "shouldStripe" : key.includes("Short")
            });
            if(groups[group]["subgroup"][0].title.includes("Long") && groups[group]["subgroup"].length == 2){
                var temp = groups[group]["subgroup"][0];
                groups[group]["subgroup"][0] = groups[group]["subgroup"][1];
                groups[group]["subgroup"][1] = temp;
            }
        }
        var a= Array(Object.keys(groups).length, null);
        for(var group in groups) {
            var color = "";
            var ordering = -1;
            switch(group.toLowerCase()){
                case "other":
                    color = "#E6DED5";
                    ordering = 3;
                    break;
                case "bond":
                    color = "#C4DFE9";
                    ordering = 1;
                    break;
                case "cash":
                    color = "#F79594";
                    ordering = 2;
                    break;
                case "stock":
                    color = "#C2CFAF";
                    ordering = 0;
                    break;
                default:
                    ordering = 0;
                    break;
            }
            groups[group]["title"] = group;
            groups[group]['color'] = color;
            for (var i in groups[group]["subgroup"]) {
                var subgroup = groups[group]["subgroup"][i];
                subgroup["percentage"] = Math.round((subgroup["percentage"] / groups[group]["total"]) * 100);
            }
            a[ordering] = groups[group];
        }
        var result = {};
        result["shouldAlternate"] = false;
        result["groups"] = a;
        return result;
    }

    constructBondType(data){
        var groups = [];
        var i = 0;
        var colors = [
          "#9CBDBE", "#C4DFE9", "#F7DDBF", "#F0D4D4", "#F79594", "#F9F1CE"
        ];
        for(var group in data){
            if(data[group] > 0){
                groups.push({
                    "title" : group,
                    "total" : data[group],
                    "subgroup" : [],
                    "color" : colors[i++]
                });
            }
        }
        var result = {};
        result["shouldAlternate"] = true;
        result["groups"] = groups;
        return result;
    }

    constructStockType(data){
        var groups = [];
        for(var group in data){
            if(data[group] > 0){
                groups.push({
                    "title" : group,
                    "total" : data[group],
                    "subgroup" : []
                });
            }
        }
        var result = {};
        result["shouldAlternate"] = true;
        result["groups"] = groups;
        return result;
    }

    getModule(){
        const module = this.props.module;
        if(!module.getData()) return null;
        var payload = {};
        switch(module.name){
            case ModuleType.HOLDING_TYPE:
                payload = this.constructHoldingType(module.getData());
                break;
            case ModuleType.STOCK_TYPE:
                payload = this.constructStockType(module.getData());
                break;
            case ModuleType.BOND_TYPE:
                payload = this.constructBondType(module.getData());
                break;
            default:
                break;
        }
        return <VestiBlock name={module.getName()} payload={payload}/>
    }

    render(){
        return(
            <div>
                {this.getModule()}
            </div>
        );
    }

}


export default AssetModuleFactory;