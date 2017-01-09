import React, {Component} from 'react';

class InfoPanel extends Component{

    constructor(props){
        super(props);
    }

    getRenewDate(){
        var subscriptionDate = new Date(this.props.dateSubscription);
        subscriptionDate.setFullYear(subscriptionDate.getFullYear() + 1);
        var today = new Date();
        var result = Math.floor((subscriptionDate - today)/ (1000 * 3600 * 24));
        return 0 ? result <=0 : result;
    }

    render(){
        return(
            <div className="card-panel">
                <div className="row">
                    <div className="col s6">
                        <h1 className="center-align participant-info-header">{this.props.employeeCount}</h1>
                    </div>
                    <div className="col s6">
                        <h1 className="center-align participant-info-header">{this.getRenewDate()}</h1>
                    </div>
                </div>
                <div className="row">
                    <div className="col s6">
                        <p className="center-align participant-info">Employees using Vestivise. </p>
                    </div>
                    <div className="col s6">
                        <p className="center-align participant-info">Days until the next renewal date.</p>
                    </div>
                </div>
            </div>
        );
    }

}


export default InfoPanel;