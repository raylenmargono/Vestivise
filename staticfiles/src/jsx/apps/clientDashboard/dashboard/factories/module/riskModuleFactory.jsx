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
                    return "Vestivise" + "<br/>" + value;
                }
                if(value == data.riskLevel){
                    return null;
                }
                return value;
            },
            gaugeLabel : data.riskLevel,
            linePositions : [2],
            stops : [
                [0, '#C6DF86'], // green
            ],
            backgroundColorGauge : "#DDDDDD"

        }
    }

    getRiskAgeProfilePayload(data){
        const stock = data.stock;
        const bond = data.bond;
        const benchStock = data.benchStock;
        const benchBond = data.benchBond;
        const avgStock = data.avgStock;
        const avgBond = data.avgBond;
        return {
            max : 100,
            min : 0,
            title : "Risk-Age",
            data : stock,
            tickPositions: [0, stock, avgStock, benchStock, 100],
            formatter : function() {
                var value = this.value.toString();
                if(value == benchStock){
                    return "Benchmark" + "<br/>" + benchStock + "% | " + benchBond + "%";
                }
                else if(value == avgStock){
                    return "Vestivise" + "<br/>" + avgStock + "% | " + avgBond + "%";
                }
                else if(value == stock) return null;
                if(value == 0) return "Stocks";
                if(value == 100) return "Bonds";
                return value + "%";
            },
            gaugeLabel : stock + "% | " + bond + "%",
            linePositions: [3, 4],
            stops : [
                [0, '#FF8788'], // green
            ],
            backgroundColorGauge : stock == 0 && bond == 0 ? "#DDDDDD" : "#95BEBE"
        }

    }

    getModule(){
        const module = this.props.module;
        if(!module.getData()) return null;
        switch(module.name){
            case ModuleType.RISK_PROFILE:
                return <VestiGauge name={module.getID()} payload={this.getRiskProfilePayload(module.getData())}/>
            case ModuleType.RISK_AGE_PROFILE:
                return <VestiGauge name={module.getID()} payload={this.getRiskAgeProfilePayload(module.getData())}/>
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