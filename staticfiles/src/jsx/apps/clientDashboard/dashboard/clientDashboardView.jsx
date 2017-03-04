import React, {Component} from 'react';
import ModuleSection from './moduleSections.jsx';
import {ModuleType} from './factories/module/moduleFactory.jsx';
import FloatingNav from './floatingNav.jsx';
import ModuleNav from './moduleNav.jsx';
import ModuleGroup from './const/moduleGroup.jsx';
import AccountManagerModal from './accountManagerModal.jsx';
import MainViewWalkThrough from 'js/walkthrough/mainViewWalkThrough';
import {Storage} from 'js/utils';
import HoldingModal from './holdingModal.jsx';
import {OtherModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';

class ClientDashboardView extends Component{

    constructor(props){
        super(props);
        this.state = {
            hideNav : false,
            startWalkThrough : false,
        }
    }

    componentDidMount(){
        window.addEventListener('scroll', this.handleScroll.bind(this));
        window.onbeforeunload = function (e) {
            if(this.props.trackingAction){
                this.props.trackingAction.trackDashboardInformation(this.props.dashboardState.moduleStacks);
            }
        }.bind(this)
    }

    componentWillReceiveProps(nextProps){
        if(this.props.dashboardState.isLoading && !nextProps.dashboardState.isLoading){
            setTimeout(function() {
                this.props.trackingAction.dashboardShown(nextProps.dashboardState.dashboardDidShow);
            }.bind(this), 10);
        }
    }

    componentDidUpdate(){
        var w = Storage.get("walkthroughProgress");
        var state = this.props.dashboardState;

        function walkthroughDone(){
            this.props.trackingAction.stopShepardTimer();
        }

        if(state.isCompleted && state.isLinked && !state.isLoading && !state.isDemo && !this.state.startWalkThrough){

            //if(!w["dashboard"]){
                this.setState({
                    startWalkThrough : true
                }, function(){
                    setTimeout(function() {
                        this.props.trackingAction.startShepardTimer();
                        MainViewWalkThrough.startWalkThrough("dashboard", walkthroughDone.bind(this));
                    }.bind(this), 10);
                });
                w["dashboard"] = true;
                Storage.put("walkthroughProgress", w);
            //}
        }
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
                    <h5>Click on <a href={Urls.settingsPage()}>Settings</a> to link/manage your account!</h5>
                </div>
            );
        }
        if(!dashboardState.isCompleted){

            function retryState(){
                this.props.dataAction.refetchProfile();
            }
            setTimeout(retryState.bind(this), 1000 * 15);
            return (
                <div id="loading-container">
                    <h5>Our number monkeys are crunching.</h5>
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
                        trackAction={this.props.trackingAction}
                    />
                </div>
                <div id="chart-returns" className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.RETURN)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                        trackAction={this.props.trackingAction}
                    />
                </div>
                <div id="chart-risks" className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.RISK)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                        trackAction={this.props.trackingAction}
                    />
                </div>
                <div id="chart-costs" className="section">
                    <ModuleSection
                        dataAction={this.props.dataAction}
                        appAction={this.props.appAction}
                        stack={this.getStack(ModuleGroup.COST)}
                        dataAPI={this.props.dashboardState.moduleAPIURL}
                        trackAction={this.props.trackingAction}
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
                <HoldingModal
                    payload={this.props.dashboardState.moduleStacks.Other.moduleMap[OtherModuleType.PORT_HOLD]}
                    isLoading={this.props.dashboardState.isLoading}
                />
                <ModuleNav/>
                <AccountManagerModal
                    dataAction={this.props.dataAction}
                    accounts={this.props.dashboardState.accounts}
                />
                <FloatingNav accounts={this.props.dashboardState.accounts} isDemo={this.props.dashboardState.isDemo}/>
                {this.getContainer()}
            </div>
        );
    }

}


export default ClientDashboardView;