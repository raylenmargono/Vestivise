import React, {Component} from 'react';
import VestiBar from 'jsx/apps/clientDashboard/dashboard/modules/vestiBar.jsx';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';


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
                name : "Benchmark",
                data : data["benchmark"]
            }
        ];
        return {
            title : "Return Amount",
            categories : [
                "One Year",
                "Two Year",
                "Three Year",

            ],
            data: payload
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
            title : "Return Amount",
            categories : [
                "One Year",
                "Two Year",
                "Three Year",

            ],
            data: payload
        };
    }

    getContributionWithdrawPayload(data){

        function clean(payload, title){
            return {
                name : title,
                data : [
                    payload["contributions"],
                    payload["withdraw"],
                    payload["net"]
                ]
            };
        }

        var result = {
            title : "$ Amount",
            categories : [
                "One Year",
                "Two Year",
                "Three Year",
            ]
        };

        result['data'] = [];
        result['data'].push(clean(data["oneYear"], "Contributions"));
        result['data'].push(clean(data["twoYear"], "Withdraws"));
        result['data'].push(clean(data["threeYear"], "Net"));
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

        return <VestiBar payload={payload}/>
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