import React, {Component} from 'react';
import Highcharts from 'highcharts';
import ModuleGroup from 'jsx/apps/clientDashboard/dashboard/const/moduleGroup.jsx';
import AssetModuleFactory from './assetModuleFactory.jsx';
import CostModuleFactory from './costModuleFactory.jsx';
import ReturnsModuleFactory from './returnsModuleFactory.jsx';
import RiskModuleFactory from './riskModuleFactory.jsx';

const themeColor = "#434778";
Highcharts.setOptions({
    chart: {
        style: {
            fontFamily: 'Graphik,Helvetica,Arial,sans-serif'
        }
    },
    legend: {
          itemStyle: {
              fontFamily: 'Graphik,Helvetica,Arial,sans-serif',
              fontWeight: '100',
              color : themeColor,
              fontSize : 15
          },
    },
    xAxis : {
        labels: {
            style: {
                color : themeColor,
                fontSize : 13
            }
        }
    },

    yAxis : {
        title: {
            style: {
                color : themeColor,
                fontSize : 13
            }
        },
        labels: {
            style: {
                color : themeColor,
                fontSize : 13
            }
        }
    }
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
