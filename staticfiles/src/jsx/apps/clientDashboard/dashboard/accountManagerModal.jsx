import React, {Component} from 'react';

class AccountManagerModal extends Component{

    constructor(props){
        super(props);
        if(!localStorage.getItem("filters")){
            localStorage.setItem("filters", JSON.stringify({}));
        }
        this.state = {
            opened : true
        }
    }

    componentDidMount(){
        $('#accountModal').modal({
            complete : function(){
                this.setState({
                    opened : false
                }, function(){
                    this.setState({
                        opened : true
                    });
                }.bind(this));
            }.bind(this)
        });
    }

    getAccounts(){
        if(!this.state.opened) return null;
        const accounts = this.props.accounts;
        var result = [];
        const filters = JSON.parse(localStorage.getItem("filters"));
        for(var i in accounts){
            const account = accounts[i];
            result.push(
                <p key={i}>
                    <input
                        ref={account.id}
                        className="filled-in checkbox-vestivise"
                        type="checkbox"
                        id={"account" + i}
                        defaultChecked={filters[account] ? "" : "checked" }
                    />
                    <label htmlFor={"account" + i}>{account.brokerage_name}</label>
                </p>
            );
        }
        return result;
    }

    handleFilter(){
        var filters = JSON.parse(localStorage.getItem("filters"));
        var accounts = this.props.accounts;
        for(var i in accounts){
            const account = accounts[i];
            var el = this.refs[account.id];
            if(el.checked && filters[account]){
                delete filters[account];
            }
            else if(!el.checked){
                filters[account] = account;
            }
        }
        localStorage.setItem("filters", JSON.stringify(filters));

        this.props.dataAction.activateFilter(filters);

        $('#accountModal').modal("close");
    }

    render(){
        return(

            <div id="accountModal" className="modal">
                <div>
                    <div className="modal-content">
                        <h4>Filter Dashboard</h4>
                        <p>Select accounts to view on dashboard</p>
                        <form>
                            {this.getAccounts()}
                        </form>
                    </div>
                    <div className="modal-footer">
                        <a onClick={this.handleFilter.bind(this)} className="max-width waves-effect waves-light btn modal-action">Update Dashboard</a>
                    </div>
                </div>
            </div>
        );
    }

}


export default AccountManagerModal;