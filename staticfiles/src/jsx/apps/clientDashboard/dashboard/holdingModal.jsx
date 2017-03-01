import React, {Component} from 'react';
import VestiTable from 'jsx/apps/clientDashboard/dashboard/modules/vestiTable.jsx';
import {toUSDCurrency} from 'js/utils';

class HoldingModal extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount() {
        $('#holdingModal').modal();
    }

    constructPortfolioHoldings(){
        var result = {
            "headers" : [],
            "rows" : []
        };
        var payload = this.props.payload;
        if(!payload || !payload['data'] || this.props.isLoading) return result;
        const data = payload.data;
        var rows = [];
        var i = 0;
        for(const holding in data["holdings"]){
            const holdingData = data["holdings"][holding];
            const isLink = holdingData["isLink"];
            const value = holdingData["value"];
            const pp = holdingData["portfolioPercent"];
            const returns = holdingData["returns"];
            const expenseRatio = holdingData["expenseRatio"];

            const el = (
                <p>
                    <input className="tableCheck filled-in" readOnly="readOnly" type="checkbox" id={i + "table"} checked={isLink ? "checked" : ""} />
                    <label htmlFor={i + "table"}></label>
                </p>
            );

            rows.push({
                "rowData":[holding, el, (pp * 100).toFixed(2) + "%", toUSDCurrency(value), returns != null ? returns + "%" : returns , expenseRatio + "%"],
                "style" : {}
            });
            i += 1;
        }
        rows.sort(function(a, b) {
            if(parseFloat(a["rowData"][2].substring(0, a["rowData"][2].length - 1)) < parseFloat(b["rowData"][2].substring(0, b["rowData"][2].length - 1))){
                return 1;
            }
            else if(parseFloat(a["rowData"][2].substring(0, a["rowData"][2].length - 1)) > parseFloat(b["rowData"][2].substring(0, b["rowData"][2].length - 1))){
                return -1;
            }

            return 0;
        });

        result["headers"] = ["Holdings", "Linked", "Weight", "Value", "Returns", "Cost"];
        result["rows"] = rows;
        return result;
    }

    render(){
        return(
            <div id="holdingModal" className="modal">
                <button className="modal-close gray btn-flat">X</button>
                <div className="modal-content">
                    <small className="small vestired-text">Holdings that are not linked may take up to 24 hours to be included in the dashboard.</small>
                    <VestiTable
                        payload={this.constructPortfolioHoldings()}
                    />
                </div>
            </div>
        );
    }

}


export default HoldingModal;