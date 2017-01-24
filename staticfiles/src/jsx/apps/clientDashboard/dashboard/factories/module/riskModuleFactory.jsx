import React, {Component} from 'react';
import VestiCategory from 'jsx/apps/clientDashboard/dashboard/modules/vestiCategory.jsx';
import VestiGauge from 'jsx/apps/clientDashboard/dashboard/modules/vestiGauge.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';

class RiskModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getRiskProfilePayload(data){
        return {
            max : 2,
            min : -2,
            title : "Risk-Return",
            data : data.riskLevel,
            tickPositions: [-2, data.averageUser, data.riskLevel, 2],
            formatter : function() {
                var value = this.value.toString();
                if(value == data.averageUser){
                    return "Vestivise" + "<br/>" + value + "%";
                }
                if(value == data.riskLevel){
                    return null;
                }
                return value;
            }
        }
    }

    getRiskAgeProfilePayload(data){
        return {
            category : data.barVal * 100,
            title : "Your risk is characterized as " + data.riskLevel,
            colors : ["#bdc3c7", "#95a5a6", "#2c3e50"],
            dialColor : "#F43E54"
        }
    }

    getModule(){
        const module = this.props.module;
        if(!module.getData()) return null;
        switch(module.name){
            case ModuleType.RISK_PROFILE:
                return <VestiGauge name={module.getID()} payload={this.getRiskProfilePayload(module.getData())}/>
            case ModuleType.RISK_AGE_PROFILE:
                return <VestiCategory name={module.getID()} payload={this.getRiskAgeProfilePayload(module.getData())}/>
            default:
                break;
        }
        return null;
    }

    render(){
        return(
            <div>
                {this.getModule()}
            </div>
        );
    }

}


export default RiskModuleFactory;