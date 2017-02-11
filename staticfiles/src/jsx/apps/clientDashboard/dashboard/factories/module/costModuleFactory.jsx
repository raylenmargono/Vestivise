import React, {Component} from 'react';
import VestiGauge from 'jsx/apps/clientDashboard/dashboard/modules/vestiGauge.jsx';
import VestiAreaLine from 'jsx/apps/clientDashboard/dashboard/modules/vestiAreaLine.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';
import {toUSDCurrency} from 'js/utils';
import VestiTable from 'jsx/apps/clientDashboard/dashboard/modules/vestiTable.jsx';

class CostModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getFeePayload(data){
        return {
            max : 2.5,
            min : 0,
            title : "Fees",
            data : data.fee,
            tickPositions: [0, data.averageFee, data.fee, 2.5],
            formatter : function() {
                var value = this.value.toString();
                if(value == data.averageFee){
                    return "Vestivise" + "<br/>" + value + "%";
                }
                if(value == 0 || value == 2.5){
                    return value + "%";
                }
            },
            gaugeLabel : data.fee + "%",
            linePositions : [2],
            stops : [
                [0.1, '#ffa724'], // green
                [0.5, '#ffdb6d'], // yellow
                [0.9, '#b8d86b'] // red
            ],
            backgroundColorGauge : "#DDDDDD"
        }
    }

    getCompoundInterestPayload(data){
        var categories = ["Now"];
        for(var i = 1 ; i < data["futureValues"].length; i++){
            categories.push(i + " Years");
        }

        var interval = data["futureValues"].length <= 10 ? 2 : 5;

        return {
            categories : categories,
            data: [
                {
                    name : "Savings",
                    data : data["futureValues"],
                    color : "#95a5a6"
                },
                {
                    name : "Savings Minus Fees",
                    data : data["futureValuesMinusFees"],
                    color : "#34495e"
                },
                {
                    name : "Savings Minus Fees and Inflation",
                    data : data["netRealFutureValue"],
                    color : "#2980b9"
                },
            ],
            minTickInterval: interval,
            yTitle : "$ Amount",
            formatter : function() {
                var value = this.y;
                return toUSDCurrency(value);
            }
        }
    }

    getModule(){
        const module = this.props.module;
        if(!module.getData()) return null;
        switch(module.name){
            case ModuleType.FEES:
                return <VestiGauge name={module.getID()} payload={this.getFeePayload(module.getData())}/>
            case ModuleType.COMPOUND_INTEREST:
                return <VestiAreaLine name={module.getID()} payload={this.getCompoundInterestPayload(module.getData())}/>
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