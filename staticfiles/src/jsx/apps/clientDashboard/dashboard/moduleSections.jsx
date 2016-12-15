import React, {Component} from 'react';
import {ModuleFactory} from './factories/module/moduleFactory.jsx';
import ReactCSSTransitionGroup from 'react-addons-css-transition-group';
import ModuleDescription from './moduleDescription.jsx';

class ModuleSection extends Component{

    constructor(props){
        super(props);
        this.state = {
            transitionState : "transitionStationary"
        }
    }

    getModule(){
        return this.props.stack.getCurrentModule();
    }

    prevModule(){
        this.setState({
           transitionState : "transitionLeftModule"
        });
        this.props.appAction.prevModule(this.props.stack.getType());
    }

    nextModule(){
        this.setState({
            transitionState : "transitionRightModule"
        });
        this.props.appAction.nextModule(this.props.stack.getType());
    }

    getTitle(){
        const mod = this.props.stack.getCurrentModule();
        if(!mod) return "Loading...";
        return mod.getName();
    }

    render(){
        return(
            <div>
                <div className="row">
                    <div className="chart-container valign-wrapper">
                        <div className="col m2 left-align">
                            <button onClick={this.prevModule.bind(this)} className="btn-flat nav-button">
                                <i className="material-icons">navigate_before</i>
                            </button>
                        </div>
                        <div className="col m8">
                            <ReactCSSTransitionGroup
                              transitionName={this.state.transitionState}
                              transitionEnterTimeout={500}
                              transitionLeaveTimeout={500}
                              transitionAppear={true}
                              transitionAppearTimeout={500}
                            >
                                <ModuleFactory
                                    dataAction={this.props.dataAction}
                                    module={this.getModule()}
                                    dataAPI={this.props.dataAPI}
                                    key={this.getTitle()}
                                />
                            </ReactCSSTransitionGroup>
                        </div>
                        <div className="col m2 right-align">
                            <button onClick={this.nextModule.bind(this)} className="btn-flat nav-button">
                                <i className="material-icons">navigate_next</i>
                            </button>
                        </div>
                    </div>
                </div>

                <ModuleDescription
                    title={this.getTitle()}
                    key={this.getTitle() + "title"}
                />


            </div>
        );
    }

}


export default ModuleSection;