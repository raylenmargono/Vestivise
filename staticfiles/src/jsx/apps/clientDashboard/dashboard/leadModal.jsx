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
        };
        API.post(Urls.subscribeToSalesList(), payload)
        .end(function(err, res){
            $('#leadModal').modal('close');
        });
    }

    render(){
        //todo add number monkey
        return(
            <div id="leadModal" className="modal">
                <button className="modal-close btn-flat upperright">X</button>
                <div className="modal-content">
                    <p id="header-lead">For more information please fill out the information below</p>
                    <div className="row">
                        <button type="submit" className="waves-effect btn valign center-block max-width">Free Sign Up</button>
                    </div>
                </div>
            </div>
        );
    }

}


export default LeadModal;