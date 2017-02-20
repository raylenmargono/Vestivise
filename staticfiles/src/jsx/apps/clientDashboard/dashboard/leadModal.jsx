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
        return(
            <div id="leadModal" className="modal">
                <button className="modal-close btn-flat upperright">X</button>
                <div className="modal-content">
                    <p id="header-lead">Quit Monkeying Around!</p>
                    <div className="row">
                        <div className="col m6 s3">
                            <img src={"/media/number-monkey-suit.png"} />
                        </div>
                        <div className="col offset-m2 m4 s9">
                            <button style={{"marginTop" : "150px"}} type="submit" className="waves-effect btn valign center-block">Free Sign Up</button>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

}


export default LeadModal;