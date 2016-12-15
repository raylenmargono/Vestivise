/**
 * Created by raylenmargono on 12/6/16.
 */
import EmployeeSource from 'js/flux/hrDashboard/sources/sources';
import {employeeSearchAction} from 'js/flux/hrDashboard/actions/actions';
import { datasource, bind, createStore } from 'alt-utils/lib/decorators';
import alt from 'js/flux/alt';

@createStore(alt)
@datasource(EmployeeSource)
class EmployeeStore{
    constructor(){
        this.state = {
            searchQuery : "",
            page : 1,
            employees : [],
            isLoading : false,
            count: 0
        };
    }

    @bind(employeeSearchAction.loadingResults)
    employeeSearchLoading(isLoading){
        this.setState({
            isLoading: isLoading
        });
    }

    @bind(employeeSearchAction.receivedResults)
    employeeSearchResults(data){
        this.setState({
            isLoading: false,
            employees : data['data'],
            count : data['count'],
            paginationCount : data['count'] % 100
        });
    }

    @bind(employeeSearchAction.fetchingResultsFailed)
    employeeSearchFailed(e){
        //alt.rollback();
        this.setState({
            isLoading: false
        });
    }

    @bind(employeeSearchAction.fetch)
    handleFetch(request){
        this.setState(request, function(){
            this.getInstance().performSearch();
        }.bind(this));
    }

}

export default EmployeeStore;
