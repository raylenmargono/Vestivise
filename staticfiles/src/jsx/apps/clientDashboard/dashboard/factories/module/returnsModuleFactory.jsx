import React, {Component} from 'react';
import VestiBar from 'jsx/apps/clientDashboard/dashboard/modules/vestiBar.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';
import {toUSDCurrency} from 'js/utils';
import VestiTable from 'jsx/apps/clientDashboard/dashboard/modules/vestiTable.jsx';


class ReturnsModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getReturnPayload(data){
        var payload = [
            {
                name : "Returns",
                data : data["returns"]
            },
            {
                name : data["benchmarkName"],
                data : data["benchmark"]
            }
        ];
        return {
            title : "% Return",
            categories : [
                "One Year",
                "Two Year",
                "Three Year",

            ],
            data: payload,
            formatter : function(){
                return '<p>' + this.y + '%</p>';
            }
        }
    }

    getReturnComparePayload(data){
        var payload = [
            {
                name : "Returns",
                data : data["returns"]
            },
            {
                name : "Average User",
                data : data["avgUser"]
            }
        ];

        return {
            title : "% Return",
            categories : [
                "One Year",
                "Two Year",
                "Three Year",

            ],
            data: payload,
            formatter : function(){
                return '<p>' + this.y + '%</p>';
            }
        };
    }

    getContributionWithdrawPayload(data){

        var result = {
            title : "$ Amount",
            categories : [
                "One Year",
                "Two Year",
                "Three Year",
            ],
            formatter : function(){
                return '<p>' + toUSDCUrrency(this.y) + '</p>';
            }
        };

        var temp = {
            "Contributions" : [],
            "Withdrawals" : [],
            "Net" : []
        };
        for(var key in data){
            if(key != "total"){
                temp["Contributions"].push(data[key]["contributions"]);
                temp["Withdrawals"].push(data[key]["withdraw"]);
                temp["Net"].push(data[key]["net"]);
            }
        }
        result['data'] = [];
        for(var key in temp){
            var value = temp[key];
            result['data'].push({
                name : key,
                data : value
            });
        }

        return result;
    }

    getModule(){

        const module = this.props.module;
        if(!module.getData()) return null;
        var payload = [];
        switch(module.getName()){
            case ModuleType.RETURNS:
                payload = this.getReturnPayload(module.getData());
                break;
            case ModuleType.CONTRIBUTION_WITHDRAW:
                payload = this.getContributionWithdrawPayload(module.getData());
                break;
            case ModuleType.RETURNS_COMPARE:
                payload = this.getReturnComparePayload(module.getData());
                break;
            default:
                break;
        }

        return <VestiBar name={module.getID()} payload={payload}/>
    }

    render(){
        return(
            <div>
                {this.getModule()}
            </div>
        );
    }

}


export default ReturnsModuleFactory;