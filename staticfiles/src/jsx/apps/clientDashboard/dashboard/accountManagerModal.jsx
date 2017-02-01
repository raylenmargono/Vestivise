import React, {Component} from 'react';
import {Storage} from 'js/utils';

class AccountManagerModal extends Component{

    constructor(props){
        super(props);

        var checked = {};
        var unchecked = {};

        if(!Storage.get("filters")){
            Storage.put("filters", {});
        }

        this.state = {
            checked : checked,
            unchecked : unchecked,
            defaultChecked : checked,
            defaultUnChecked : unchecked
        }
    }

    componentDidMount(){
        $('#accountModal').modal({
            complete : function(){
                var dc = Object.assign({}, this.state.defaultChecked);
                var du = Object.assign({}, this.state.defaultUnChecked);
                this.setState({
                    checked : dc,
                    unchecked : du
                });
            }.bind(this)
        });
    }

    componentWillReceiveProps(nextProps){
        if(Object.keys(this.state.defaultUnChecked).length == 0 && Object.keys(this.state.checked).length == 0 && nextProps.accounts.length != 0 && this.props.accounts.length == 0){
            var filters = Storage.get("filters");
            var checked = {};
            var unchecked = {};
            var defaultChecked = {};
            var defaultUnChecked = {};
            const accounts = nextProps.accounts;
            for(var i in accounts){
                const account = accounts[i];
                const isUnChecked = filters[account.id];
                if(isUnChecked){
                    unchecked[account.id] = account;
                    defaultUnChecked[account.id] = account;
                }
                else {
                    defaultChecked[account.id] = account;
                    checked[account.id] = account;
                }

                this.setState({
                    checked : checked,
                    unchecked : unchecked,
                    defaultChecked : defaultChecked,
                    defaultUnChecked : defaultUnChecked
                });
            }
        }
    }

    handleCheck(account){
        var checked = this.state.checked;
        var unchecked = this.state.unchecked;
        if(checked[account.id] && Object.keys(checked).length > 1){
            delete checked[account.id];
            unchecked[account.id] = account;
        }
        else if(unchecked[account.id]){
            delete unchecked[account.id];
            checked[account.id] = account;
        }

        this.setState({
            checked : checked,
            unchecked : unchecked
        });
    }

    getAccounts(){
        const accounts = this.props.accounts;
        var result = [];
        const checked = this.state.checked;
        for(var i in accounts){
            const account = accounts[i];
            result.push(
                <p key={i}>
                    <input
                        ref={account.id}
                        className="filled-in checkbox-vestivise"
                        type="checkbox"
                        id={"account" + i}
                        checked={checked[account.id] ? "checked" : "" }
                        onChange={this.handleCheck.bind(this, account)}
                    />
                    <label htmlFor={"account" + i}>{account.brokerage_name}</label>
                </p>
            );
        }
        return result;
    }

    handleFilter(){
        var filters = Storage.get("filters");
        var accounts = this.props.accounts;
        for(var i in accounts){
            const account = accounts[i];
            var el = this.refs[account.id];
            if(el.checked && filters[account.id]){
                delete filters[account.id];
            }
            else if(!el.checked){
                filters[account.id] = account;
            }
        }

        Storage.put("filters", filters);

        var dc = Object.assign({}, this.state.checked);
        var du = Object.assign({}, this.state.unchecked);
        this.setState({
            checked : this.state.checked,
            unchecked : this.state.unchecked,
            defaultChecked : dc,
            defaultUnChecked : du
        });

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