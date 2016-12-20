/**
 * Created by raylenmargono on 12/6/16.
 */
import EmployeeSource from 'js/flux/hrDashboard/sources/sources';
import {EmployeeSearchAction, EmployeeEditAction} from 'js/flux/hrDashboard/actions/actions';
import { datasource, bind, createStore } from 'alt-utils/lib/decorators';
import alt from 'js/flux/alt';

@createStore(alt)
@datasource(EmployeeSource)
class HRDashboardStore{
    constructor(){
        this.state = {
            searchQuery : "",
            page : 1,
            employees : [],
            isLoading : false,
            employeeCount: 0,
            paginationCount : 0
        };
    }

    @bind(EmployeeSearchAction.loadingResults)
    employeeSearchLoading(isLoading){
        this.setState({
            isLoading: isLoading
        });
    }

    @bind(EmployeeSearchAction.receivedResults)
    employeeSearchResults(data){
        this.setState({
            isLoading: false,
            employees : data['data'],
            employeeCount : data['count'],
            paginationCount : data['count'] % 100
        });
    }

    @bind(EmployeeSearchAction.fetchingResultsFailed)
    employeeSearchFailed(e){
        //alt.rollback();
        this.setState({
            isLoading: false
        });
    }

    @bind(EmployeeSearchAction.fetch)
    handleFetch(request){
        this.setState(request, function(){
            this.getInstance().performSearch();
        }.bind(this));
    }

}

export default HRDashboardStore;
