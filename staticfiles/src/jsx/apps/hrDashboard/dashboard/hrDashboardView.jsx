import React, {Component} from 'react';
import FloatingNav from './floatingNav.jsx';
import SearchBar from './searchBar.jsx';
import AddUsersButton from './addUsersButton.jsx';
import EmployeeTable from './employeeTable.jsx';
import InfoPanel from './infoPanel.jsx';

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
        this.setState({
           hideNav : scroll_top > 30
        });
    }

    render(){
        return(
            <div className={this.getScrollStateContainer()} >
                <FloatingNav/>
                <div className="row margin-row"></div>
                <div className="row">
                    <div className="section">
                        <h5 className="white-text">Welcome {this.props.ProfileState.companyName}</h5>
                    </div>
                </div>
                <div className="row valign-wrapper">
                    <div className="col m8 input-field valign">
                        <SearchBar
                            searchAction={this.props.EmployeeSearchAction}
                        />
                    </div>

                    <div className="col m3 offset-m4">
                        <AddUsersButton
                            editAction={this.props.EmployeeEditAction}
                        />
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
            </div>
        );
    }

}


export default HRDashboard;