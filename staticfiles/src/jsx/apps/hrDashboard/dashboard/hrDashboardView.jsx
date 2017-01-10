import React, {Component} from 'react';
import FloatingNav from './floatingNav.jsx';
import SearchBar from './searchBar.jsx';
import ActionModal from './actionModalViews/actionModal.jsx';
import EmployeeTable from './employeeTable.jsx';
import InfoPanel from './infoPanel.jsx';
import {GroupActions} from "./actionModalViews/actionModal.jsx";

class HRDashboard extends Component{

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
        var result = "container";
        if(this.state.hideNav){
            result += " scroll";
        }
        return result;
    }

    handleScroll(){
        var scroll_top = $(window).scrollTop();
        if(scroll_top > 30 != this.state.hideNav){
            this.setState({
               hideNav : scroll_top > 30
            });
        }
    }

    addUserAction(){
        this.props.EmployeeEditAction.modalOption({
            action : GroupActions.List
        });
    }

    render(){
        return(
            <div className={this.getScrollStateContainer()} >
                <FloatingNav/>
                <div className="row margin-row"></div>
                <div className="row">
                    <div className="section">
                        <h5 id="welcome-text">Welcome {this.props.ProfileState.companyName}</h5>
                    </div>
                </div>
                <div className="row valign-wrapper">
                    <div className="col m8 input-field valign">
                        <SearchBar
                            searchAction={this.props.EmployeeSearchAction}
                        />
                    </div>

                    <div className="col m3 offset-m4">
                        <button onClick={this.addUserAction.bind(this)} data-target="edit-modal" id="add-user-button" className="waves-effect waves-light btn">
                            Add Users
                        </button>
                    </div>
                </div>
                <div className="row">
                    <div className="col m12">
                        <EmployeeTable
                            paginationCount={this.props.AppState.paginationCount}
                            employees={this.props.AppState.employees}
                            currentPage={this.props.AppState.page}
                            employeeCount={this.props.AppState.employeeCount}
                            searchAction={this.props.EmployeeSearchAction}
                            searchQuery={this.props.AppState.searchQuery}
                            editAction={this.props.EmployeeEditAction}
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="col s12">
                        <h4 className="header">Participant Info</h4>
                        <InfoPanel
                            employeeCount={this.props.AppState.employeeCount}
                            dateSubscription={this.props.ProfileState.renewalDate}
                        />
                    </div>
                </div>
                <ActionModal
                    editAction={this.props.EmployeeEditAction}
                    isLoading={this.props.AppState.editLoading}
                    editResponse={this.props.AppState.editResponse}
                    modalActionData={this.props.AppState.modalActionData}
                />
            </div>
        );
    }

}


export default HRDashboard;