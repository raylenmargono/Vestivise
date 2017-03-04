/**
 * Created by raylenmargono on 2/26/17.
 */
import {TrackingAction} from 'js/flux/clientDashboard/actions/actions';


class TrackingDataStore{

    constructor(){
        this.state = {
            dashboardClientHasShown : false,
            dashboardViewTime : new Date().getTime(),
            tutorialTime : 0,
        };
        this.bindListeners({
            startShepardTimer : TrackingAction.startShepardTimer,
            stopShepardTimer : TrackingAction.stopShepardTimer,
            trackDashboardInformation : TrackingAction.trackDashboardInformation,
        });
    }

    startShepardTimer(didStart){
        this.setState({
           tutorialTime : new Date().getTime()
        });
    }

    stopShepardTimer(didStop){
        var tutorialTime = Math.abs(new Date().getTime() - this.state.tutorialTime) / 1000;
        TrackingAction.trackAction("tutorial_time", tutorialTime);
    }

    trackDashboardInformation(modules){
        var dashboardViewTime = Math.abs(new Date().getTime() - this.state.dashboardViewTime) / 1000;
        TrackingAction.trackAction("total_dashboard_view_time", dashboardViewTime);
        TrackingAction.trackAction("module_view", {
            "modules" : modules
        });
        return;
    }

}

export default TrackingDataStore;
