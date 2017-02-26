import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import ClientDashboardView from '../dashboard/clientDashboardView.jsx';
import AltContainer from 'alt-container';
import {ClientDashboardStore, DemoDashboardStore} from 'js/flux/clientDashboard/stores/clientDashboardStore';
import TrackingDataStore from 'js/flux/clientDashboard/stores/trackingDataStore';
import  {ClientAppAction, ClientDataAction, TrackingAction} from 'js/flux/clientDashboard/actions/actions';
import alt from 'js/flux/alt';
import LeadModal from '../dashboard/leadModal.jsx';
import {Storage} from 'js/utils';

var appStore = null;

if(isDemo){
    appStore = alt.createStore(DemoDashboardStore);
}
else{
    appStore = alt.createStore(ClientDashboardStore);
}

if(!Storage.get("walkthroughProgress") && !isDemo){
    var o = {
        "linkage" : false,
        "dashboard" : false,
    };
    Storage.put("walkthroughProgress", o);
}

var stores = {
    dashboardState : appStore
};

var actions = {
    appAction : ClientAppAction,
    dataAction : ClientDataAction,
    trackingAction : null
};

if(!isDemo){
    stores["trackingState"] = alt.createStore(TrackingDataStore);
    actions["trackingAction"] = TrackingAction;
}


class App extends Component {

    componentDidMount() {
        appStore.getProfileFetch();
    }

    render() {
        return (
            <div>
                <AltContainer
                    actions = {
                        actions
                    }
                    stores = {
                        stores
                    }
                >
                    <ClientDashboardView/>
                </AltContainer>
                {isDemo ? <LeadModal/> : null}
            </div>
        );
    }
}

ReactDOM.render(<App/>, document.getElementById("app"));