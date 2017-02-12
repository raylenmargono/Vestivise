import React, {Component} from 'react';
import API from 'js/api';
import {getCookie} from 'js/utils';


class LeadModal extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount() {
        if(getCookie("demo_access") !== "True"){
            window.setTimeout(function(){
                $('#leadModal').modal({
                    dismissible : false,
                });
                $('#leadModal').modal('open');
            }, 20000);
        }
    }

    submitLead(e){
        e.preventDefault();
        const name = this.refs.name.value;
        const company = this.refs.company.value;
        const email = this.refs.email.value;
        const payload = {
            name : name,
            company : company,
            email : email
        }
        API.post(Urls.subscribeToSalesList(), payload)
        .end(function(err, res){
            $('#leadModal').modal('close');
        });
    }

    render(){
        return(
            <div id="leadModal" className="modal">
                <button className="modal-close btn-flat upperright">X</button>
                <div className="modal-content">
                    <p id="header-lead">For more information please fill out the information below</p>
                    <div className="row">
                        <form onSubmit={this.submitLead.bind(this)} className="col s12">
                            <div className="row">
                                <div className="input-field col s12">
                                    <i className="material-icons prefix">perm_identity</i>
                                    <input placeholder="Name" ref="name" type="text" className="validate" required/>
                                </div>
                                <div className="input-field col s12">
                                    <i className="material-icons prefix">supervisor_account</i>
                                    <input placeholder="Company" ref="company" type="text" className="validate" required/>
                                </div>
                                <div className="input-field col s12">
                                    <i className="material-icons prefix">email</i>
                                    <input placeholder="Email" ref="email" type="email" className="validate" required/>
                                </div>
                                <div className="input-field col s12">
                                    <button type="submit" className="waves-effect btn valign center-block max-width">Submit</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        );
    }

}


export default LeadModal;