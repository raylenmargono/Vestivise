import React, {Component} from 'react';
import VestiGauge from 'jsx/apps/clientDashboard/dashboard/modules/vestiGauge.jsx';
import VestiAreaLine from 'jsx/apps/clientDashboard/dashboard/modules/vestiAreaLine.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';

class CostModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getFeePayload(data){
        return {
            max : 2.5,
            min : 0,
            title : "Fees",
            data : data.fee
        }
    }

    getCompoundInterest(data){
        return {
            categories : [
                '5 Years',
                '10 Years',
                '15 Years',
                '20 Years',
                '25 Years',
                '30 Years'
            ],
            data: [
                {
                    name : "Savings",
                    data : data["futureValue"],
                    color : "#95a5a6"
                },
                {
                    name : "Savings Minus Fees",
                    data : data["futureValueMinusFees"],
                    color : "#34495e"
                },
                {
                    name : "Savings Minus Fees and Inflation",
                    data : data["NetRealFutureValue"],
                    color : "#2980b9"
                }
            ]
        }
    }

    getModule(){
        const module = this.props.module;
        if(!module.getData()) return null;
        switch(module.name){
            case ModuleType.FEES:
                return <VestiGauge payload={this.getFeePayload(module.getData())}/>
            case ModuleType.COMPOUND_INTEREST:
                return <VestiAreaLine payload={this.getCompoundInterest(module.getData())}/>
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


export default CostModuleFactory;