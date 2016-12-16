import React, {Component} from 'react';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';

class DescriptionFactory extends Component{

    constructor(props){
        super(props);
    }
    
    getDescription(){
        var module = this.props.module;
        if(!module) return;
        var moduleName = module.getName();
        var text = null;
        switch(moduleName){
            case ModuleType.RETURNS:
                break;
            case ModuleType.CONTRIBUTION_WITHDRAW:
                break;
            case ModuleType.RETURNS_COMPARE:
                break;
            case ModuleType.FEES:
                break;
            case ModuleType.COMPOUND_INTEREST:
                break;
            case ModuleType.HOLDING_TYPE:
                break;
            case ModuleType.STOCK_TYPE:
                break;
            case ModuleType.BOND_TYPE:
                break;
            case ModuleType.RISK_PROFILE:
                break;
            case ModuleType.RISK_AGE_PROFILE:
                break;
            case ModuleType.RISK_COMPARE:
                break;
            default:
                break;
        }
        return text;
    }

    getSubHeader(){
        var module = this.props.module;
        if(!module) return;
        var moduleName = module.getName();
        var text = null;
        switch(moduleName){
            case ModuleType.RETURNS:
                return 'Your returns are compared to your age based benchmark fund (X) that consists of X% and X% bonds.';
            case ModuleType.CONTRIBUTION_WITHDRAW:
                return 'Over the past four years you have contributed $X, you have withdrawn $X, and you have netted a positive/negative $X.';
            case ModuleType.RETURNS_COMPARE:
                return 'Your age group for comparisons with Vestivise users is X-X.';
            case ModuleType.FEES:
                return 'Your fees are X than the average investor.';
            case ModuleType.COMPOUND_INTEREST:
                return 'At your current rate of returns, contributions, and fees, you will have $X at retirement age adjusted for inflation. This does not account for taxes.';
            case ModuleType.HOLDING_TYPE:
                return 'You have $X invested across X asset types.';
            case ModuleType.STOCK_TYPE:
                return 'Your portfolio is X% stocks spread across X types. ';;
            case ModuleType.BOND_TYPE:
                return 'Your portfolio is X% bonds spread across X types.';
            case ModuleType.RISK_PROFILE:
                return 'Your risk-return profile is characterized as X.';
            case ModuleType.RISK_AGE_PROFILE:
                return 'Your risk-age profile is characterized as X.';
            case ModuleType.RISK_COMPARE:
                return 'Your age group for comparisons with Vestivise users is X-X.';
            default:
                break;
        }
    }

    render(){
        return(
            <div className="row">
                <div className="col m4">
                    <h5>{this.props.title}: {this.getSubHeader()}</h5>
                    <p className="grey-text">{this.getDescription()}</p>
                </div>
            </div>
        );
    }

}


export default DescriptionFactory;