import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import ClientDashboardView from '../dashboard/clientDashboardView.jsx';
import AltContainer from 'alt-container';
import {ClientDashboardStore, DemoDashboardStore} from 'js/flux/clientDashboard/stores/clientDashboardStore';
import  {ClientAppAction, ClientDataAction} from 'js/flux/clientDashboard/actions/actions';
import alt from 'js/flux/alt';

var appStore = null;

if(isDemo){
    appStore = alt.createStore(DemoDashboardStore);
}
else{
    appStore = alt.createStore(ClientDashboardStore);
}

class App extends Component {

    componentDidMount() {
        appStore.getProfileFetch();
    }

    render() {
        return (
            <AltContainer
                actions = {
                    {
                        appAction : ClientAppAction,
                        dataAction : ClientDataAction
                    }
                }
                stores = {
                    {
                        dashboardState : appStore
                    }
                }
            >
                <ClientDashboardView/>
            </AltContainer>
        );
    }
}

ReactDOM.render(<App/>, document.getElementById("app"));