import React, {Component} from 'react';
import ModuleSection from './moduleSections.jsx';
import {ModuleType} from './moduleFactory.jsx';
import FloatingNav from './floatingNav.jsx';
import ChartSlider from './chartSlider.jsx';
import ReactCSSTransitionGroup from 'react-addons-css-transition-group';

class ClientDashboardView extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div>
                <FloatingNav />
                <div id="buffer-row"></div>
                <div className="section">
                    <ReactCSSTransitionGroup
                        transitionName={""}
                        transitionEnterTimeout={500}
                        transitionLeaveTimeout={500}
                    >
                        <ModuleSection type={ModuleType.BLOCKS} />
                    </ReactCSSTransitionGroup>
                </div>
                <div className="section">
                    <ModuleSection type={ModuleType.BAR} />
                </div>
                <div className="section">
                    <ModuleSection type={ModuleType.CATEGORY} />
                </div>
                <div className="section">
                    <ModuleSection type={ModuleType.GAUGE} />
                </div>
                <ChartSlider />
            </div>
        );
    }

}


export default ClientDashboardView;