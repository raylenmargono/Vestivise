/**
 * Created by raylenmargono on 12/10/16.
 */
import API from 'js/api';
import {ClientDataAction} from 'js/flux/clientDashboard/actions/actions';

const DataSource = {
    getProfileFetch: {
        // remotely fetch something (required)
        remote(state){
            return API.get(state.profileAPIURL());
        },

        // this function checks in our local cache first
        // if the value is present it'll use that instead (optional).
        // local(state) {
        //     return state.results[state.value] ? state.results : null;
        // },

        // here we setup some actions to handle our response
        loading: ClientDataAction.loadingResults, // (optional)
        success: ClientDataAction.recievedProfileResults, // (required)
        error: ClientDataAction.fetchingProfileResultsFailed, // (required)
    }
};

const ModuleSource = {
    fetch : function(api, endpoint, filters){
        return API.get(api(endpoint), {filters : filters});
    }
};

export {DataSource, ModuleSource};