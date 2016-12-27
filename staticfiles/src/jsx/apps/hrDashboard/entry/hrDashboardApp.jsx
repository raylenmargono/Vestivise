import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import HRDashboard from '../dashboard/hrDashboardView.jsx';
import AltContainer from 'alt-container';
import HRAppStore from 'js/flux/hrDashboard/stores/hrDashboardStore';
import HRProfileStore from 'js/flux/hrDashboard/stores/userProfileStore';
import {EmployeeSearchAction, EmployeeEditAction} from 'js/flux/hrDashboard/actions/actions';

class App extends Component {

    constructor(props) {
        super(props);
    }

    componentDidMount() {
        HRAppStore.performSearch(1, "");
        HRProfileStore.performSearch();
    }

    render(){
        return(
            <AltContainer
                actions = {
                    {
                        EmployeeEditAction : EmployeeEditAction,
                        EmployeeSearchAction : EmployeeSearchAction,
                    }
                }
                stores = {
                    {
                        AppState : HRAppStore,
                        ProfileState : HRProfileStore
                    }
                }
            >
                <HRDashboard />
            </AltContainer>
        );
    }

}

ReactDOM.render(<App/>, document.getElementById("app"));