import React, {Component} from 'react';
import VestiCategory from 'jsx/apps/clientDashboard/dashboard/modules/vestiCategory.jsx';
import VestiBell from 'jsx/apps/clientDashboard/dashboard/modules/vestiBell.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';

class RiskModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getRiskProfilePayload(data){
        return {
            category : data.barVal * 100,
            title : "Your risk is characterized as " + data.riskLevel,
            colors : ["#FFA724", "#FFDB6D", "#B8D86B"]
        }
    }

    getRiskAgeProfilePayload(data){
        return {
            category : data.barVal * 100,
            title : "Your risk is characterized as " + data.riskLevel,
            colors : ["#bdc3c7", "#95a5a6", "#2c3e50"]
        }
    }

    riskComparisonPayload(data){
        return {
            sigma : data.std,
            mean : data.mean,
            title : "Risk Among Users",
            user : data.user,
            xTitle : "Risk-Return Level",
            yTitle : "Distribution"
        }
    }

    getModule(){
        const module = this.props.module;
        if(!module.getData()) return null;
        switch(module.name){
            case ModuleType.RISK_PROFILE:
                return <VestiCategory payload={this.getRiskProfilePayload(module.getData())}/>
            case ModuleType.RISK_AGE_PROFILE:
                return <VestiCategory payload={this.getRiskAgeProfilePayload(module.getData())}/>
            case ModuleType.RISK_COMPARE:
                return <VestiBell payload={this.riskComparisonPayload(module.getData())}/>
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