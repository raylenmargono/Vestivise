/**
 * Created by raylenmargono on 12/6/16.
 */
import API from 'js/api';
import {EmployeeSearchAction, EmployeeEditAction, HRProfileActions} from 'js/flux/hrDashboard/actions/actions';

const EmployeeSource = {
    performSearch: {
        // remotely fetch something (required)
        remote(state, page, searchQuery){
            const query = {
                "page_size" : "max",
                "page" : page,
                "search_query" : searchQuery
            }
            return API.get(Urls["companyEmployeeManagement-list"](), query);
        },

        // this function checks in our local cache first
        // if the value is present it'll use that instead (optional).
        // local(state) {
        //     return state.results[state.value] ? state.results : null;
        // },

        // here we setup some actions to handle our response
        loading: EmployeeSearchAction.loadingResults, // (optional)
        success: EmployeeSearchAction.receivedResults, // (required)
        error: EmployeeSearchAction.fetchingResultsFailed, // (required)

        interceptResponse(data, action, args) {
            if(!data) return null;
            return {
                data : data.body,
                query : args[1],
                page : args[0]
            };
        }
    }
};

const HRProfileSource = {
    performSearch: {
        // remotely fetch something (required)
        remote(state){
            return API.get(Urls.hrMe());
        },

        // this function checks in our local cache first
        // if the value is present it'll use that instead (optional).
        // local(state) {
        //     return state.results[state.value] ? state.results : null;
        // },

        // here we setup some actions to handle our response
        loading: HRProfileActions.loadingResults, // (optional)
        success: HRProfileActions.receivedResults, // (required)
        error: HRProfileActions.fetchingResultsFailed, // (required)

    }
}

export {HRProfileSource, EmployeeSource};