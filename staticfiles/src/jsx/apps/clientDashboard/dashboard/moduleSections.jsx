import React, {Component} from 'react';
import {ModuleFactory} from './moduleFactory.jsx';


class ModuleSection extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div>
                <div className="row">
                    <div className="chart-container valign-wrapper">
                        <div className="col m2 left-align">
                            <button className="btn-flat nav-button">
                                <i className="material-icons">navigate_before</i>
                            </button>
                        </div>
                        <div className="col m8">
                            <ModuleFactory type={this.props.type} />
                        </div>
                        <div className="col m2 right-align">
                            <button className="btn-flat nav-button">
                                <i className="material-icons">navigate_next</i>
                            </button>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="col m4">
                        <h5>Section 1</h5>
                        <p className="grey-text">SStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStufftuff</p>
                    </div>
                </div>
            </div>
        );
    }

}


export default ModuleSection;