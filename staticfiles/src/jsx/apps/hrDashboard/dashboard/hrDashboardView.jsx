import React, {Component} from 'react';
import FloatingNav from './floatingNav.jsx';
import SearchBar from './searchBar.jsx';
import AddUsersButton from './addUsersButton.jsx';
import EmployeeTable from './employeeTable.jsx';
import InfoPanel from './infoPanel.jsx';
import HRAppStore from 'js/flux/hrDashboard/stores/hrDashboardStore';

class HRDashboard extends Component{

    constructor(props){
        super(props);
        this.state = {
            hideNav : false
        }
    }

    componentDidMount(){
        HRAppStore.performSearch();
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
        this.setState({
           hideNav : scroll_top > 30
        });
    }

    render(){
        return(
            <div className={this.getScrollStateContainer()} >
                <FloatingNav/>
                <div id="app-container" className="row margin-row valign-wrapper">
                    <div className="col m8 input-field valign">
                        <SearchBar />
                    </div>

                    <div className="col m3 offset-m4">
                        <AddUsersButton/>
                    </div>
                </div>
                <div className="row">
                    <div className="col m12">
                        <EmployeeTable
                            paginationCount={this.props.AppState.paginationCount}
                            employees={this.props.AppState.employees}
                            currentPage={this.props.AppState.page}
                            employeeCount={this.props.AppState.employeeCount}
                        />
                    </div>
                </div>
                <div className="row">
                    <div className="col s12">
                        <h4 className="header">Participant Info</h4>
                        <InfoPanel />
                    </div>
                </div>
            </div>
        );
    }

}


export default HRDashboard;