import React, {Component} from 'react';
import ModuleSection from './moduleSections.jsx';
import {ModuleType} from './factories/module/moduleFactory.jsx';
import FloatingNav from './floatingNav.jsx';
import ModuleNav from './moduleNav.jsx';
import ModuleGroup from './const/moduleGroup.jsx';

class ClientDashboardView extends Component{

    constructor(props){
        super(props);
        this.state = {
            hideNav : false
        }
    }


    componentDidMount(){
        window.addEventListener('scroll', this.handleScroll.bind(this));
    }

    getScrollStateContainer(){
        return this.state.hideNav ? "scroll" : "";
    }

    getStack(stack){
        return this.props.dashboardState.moduleStacks[stack];
    }

    handleScroll(){
        var scroll_top = $(window).scrollTop();
        this.setState({
           hideNav : scroll_top > 30
        });
    }

    getContainer(){
        const dashboardState = this.props.dashboardState;
        if(dashboardState.isLoading){
            return (
                <div id="loading-container">
                    <div className="sk-wave">
                        <div className="sk-rect sk-rect1"></div>
                        <div className="sk-rect sk-rect2"></div>
                        <div className="sk-rect sk-rect3"></div>
                        <div className="sk-rect sk-rect4"></div>
                        <div className="sk-rect sk-rect5"></div>
                    </div>
                </div>
            );
        }
        if(!dashboardState.isLinked){
            return(
                <div id="loading-container">
                    <h5> Looks like you haven't linked an account yet.</h5>
                    <h5>Click on <a href={Urls.linkAccountPage()}>Settings</a> to link/manage your account!</h5>
                </div>
            );
        }
        if(!dashboardState.isCompleted){
            return (
                <div id="loading-container">
                    <h5> Our number monkeys are crunching - check back in a day or so.</h5>
                    <div className="progress">
                        <div className="indeterminate"></div>
                    </div>
                </div>
            );
        }

        return(
            <div>
                <div id="buffer-row"></div>
                <div id="chart-assets"  className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.ASSET)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                    />
                </div>
                <div id="chart-returns" className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.RETURN)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                    />
                </div>
                <div id="chart-risks" className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.RISK)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                    />
                </div>
                <div id="chart-costs" className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.COST)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                    />
                </div>
                <ul id="slide-out" className="side-nav">
                    <li>
                        <div>
                            {this.props.dashboardState.navElement}
                        </div>
                    </li>
                </ul>
                <div className="col m12">
                    <div className="valign-wrapper">
                        <a className="valign center-block grey-text" href="http://www.vestivise.com/terms">Terms of Use</a>
                    </div>
                </div>
            </div>
        );
    }

    render(){
        return(
            <div className={this.getScrollStateContainer()}>
                <ModuleNav/>
                <FloatingNav isDemo={this.props.dashboardState.isDemo}/>
                {this.getContainer()}
            </div>
        );
    }

}


export default ClientDashboardView;