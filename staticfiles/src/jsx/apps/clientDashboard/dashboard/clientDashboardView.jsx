import React, {Component} from 'react';
import ModuleSection from './moduleSections.jsx';
import {ModuleType} from './factories/module/moduleFactory.jsx';
import FloatingNav from './floatingNav.jsx';
import ChartSlider from './chartSlider.jsx';
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

    render(){
        return(
            <div className={this.getScrollStateContainer()}>
                <FloatingNav isDemo={this.props.dashboardState.isDemo}/>
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
                <ChartSlider />
            </div>
        );
    }

}


export default ClientDashboardView;