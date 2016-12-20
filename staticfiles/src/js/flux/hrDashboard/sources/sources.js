/**
 * Created by raylenmargono on 12/6/16.
 */
import API from 'js/api';
import {EmployeeSearchAction, EmployeeEditAction} from 'js/flux/hrDashboard/actions/actions';

const EmployeeSource = {
    performSearch: {
        // remotely fetch something (required)
        remote(state){
            const searchQuery = state.searchQuery;
            const page = state.searchPage;
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

    }
};

export default EmployeeSource;