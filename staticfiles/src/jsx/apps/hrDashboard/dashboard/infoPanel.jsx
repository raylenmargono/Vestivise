import React, {Component} from 'react';

class InfoPanel extends Component{

    constructor(props){
        super(props);
    }


    render(){
        return(
            <div className="card-panel">
                <div className="row">
                    <div className="col s6">
                        <h1 className="center-align participant-info-header">Test</h1>
                    </div>
                    <div className="col s6">
                        <h1 className="center-align participant-info-header">Test</h1>
                    </div>
                </div>
                <div className="row">
                    <div className="col s6">
                        <p className="participant-info">Test</p>
                    </div>
                    <div className="col s6">
                        <p className="participant-info">Test</p>
                    </div>
                </div>
            </div>
        );
    }

}


export default InfoPanel;