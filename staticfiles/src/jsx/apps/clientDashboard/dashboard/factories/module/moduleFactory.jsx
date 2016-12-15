import React, {Component} from 'react';
import Highcharts from 'highcharts';
import ModuleGroup from 'jsx/apps/clientDashboard/dashboard/const/moduleGroup.jsx';
import AssetModuleFactory from './assetModuleFactory.jsx';
import CostModuleFactory from './costModuleFactory.jsx';
import ReturnsModuleFactory from './returnsModuleFactory.jsx';
import RiskModuleFactory from './riskModuleFactory.jsx';

Highcharts.setOptions({
    chart: {
        style: {
            fontFamily: 'Graphik,Helvetica,Arial,sans-serif'
        }
    },
    legend: {
          itemStyle: {
              fontFamily: 'Graphik,Helvetica,Arial,sans-serif',
              fontWeight: '100'
          },
    },
});

class ModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getModule(){
        var module = this.props.module;

        if(!module) return null;

        switch(module.category){
            case ModuleGroup.ASSET:
                return <AssetModuleFactory module={module}/>;
            case ModuleGroup.COST:
                return <CostModuleFactory module={module}/>;
            case ModuleGroup.RETURN:
                return <ReturnsModuleFactory module={module}/>;
            case ModuleGroup.RISK:
                return <RiskModuleFactory module={module}/>;
            default:
                return null;
        }
    }

    render(){
        return(
            <div>
                {this.getModule()}
            </div>
        );
    }

}

export {ModuleFactory};
