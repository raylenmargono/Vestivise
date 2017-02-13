/**
 * Created by raylenmargono on 12/6/16.
 */
import {EmployeeSource} from 'js/flux/hrDashboard/sources/sources';
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
            paginationCount : 0,
            editResponse : null,
            modalActionData : {},
        };
    }

    @bind(EmployeeEditAction.modalOption)
    modalOption(data){
        this.setState({
           modalActionData : data
        });
    }

    @bind(EmployeeEditAction.resetEditState)
    resetEditState(reset){
        this.setState({
            editResponse : null,
            modalActionData : {},
        });
    }

    @bind(EmployeeEditAction.loadingResults)
    employeeEditLoading(isLoading){
        this.setState({
           editLoading : true
        });
    }

    @bind(EmployeeEditAction.receivedResults)
    employeeEditReceivedResults(data){
        var currentUsersOnDisplay = this.state.employees;
        var employeeCount = this.state.employeeCount + data["success"].length;
        var paginationCount = employeeCount < 100 ? 1 : employeeCount / 100;
        if(paginationCount == this.state.page){
            currentUsersOnDisplay = currentUsersOnDisplay.concat(data["success"]);
            currentUsersOnDisplay = currentUsersOnDisplay.sort(function(a, b){
                if(a.email < b.email){
                    return -1;
                }
                if(a.email > b.email){
                    return 1;
                }
                return 0;
            });
        }
        this.setState({
            editLoading: false,
            editResponse : {
                errors : data["errors"],
                success: data["success"]
            },
            employeeCount: employeeCount,
            paginationCount : paginationCount,
            employees : currentUsersOnDisplay
        });
    }

    @bind(EmployeeEditAction.fetchingResultsFailed)
    employeeEditFailed(data){
        var payload = {
            editLoading : false
        };
        //single upload
        if("singleFail" in data){
            payload["editResponse"] = {
                "errors" : data["errors"],
                "success" : []
            }
        }
        else{
            payload["editResponse"] = {
                "errorMessage" : "Internal error occurred. Contact support@vestivise.com",
                "internalError" : true,
                "errors" : [],
                "success" : []
            }

        }
        this.setState(payload);
    }


    @bind(EmployeeSearchAction.loadingResults)
    employeeSearchLoading(isLoading){
        this.setState({
            isLoading: isLoading
        });
    }

    @bind(EmployeeSearchAction.receivedResults)
    employeeSearchResults(payload){
        const data = payload.data;
        const page = payload.page;
        const query = payload.query;
        this.setState({
            isLoading: false,
            employees : data['data'],
            employeeCount : data['count'],
            paginationCount : data['count'] < 100 ? 1 : data['count'] / 100,
            page: page,
            searchQuery: query
        });
    }

    @bind(EmployeeSearchAction.fetchingResultsFailed)
    employeeSearchFailed(e){
        //alt.rollback();
        this.setState({
            isLoading: false
        });
    }


    @bind(EmployeeSearchAction.paginate)
    handlePagination(index){
        if (!this.getInstance().isLoading()) {
            this.getInstance().performSearch(index);
        }
    }

    @bind(EmployeeSearchAction.search)
    handleQuery(query){
        if (!this.getInstance().isLoading()) {
            this.getInstance().performSearch(1, query);
        }
    }

    @bind(EmployeeEditAction.sendLinkResponse)
    handleLinkSendResponse(response){
        this.setState({
            editLoading : false,
            modalActionData : {},
            editResponse : {
                errors : response ? false : true,
                success: response ? true : false
            },
        });
    }

    @bind(EmployeeEditAction.deleteUserResponse)
    handleDeleteUserResponse(result){
        var index = result.index;
        var employees = this.state.employees;
        employees.splice(index, 1);
        this.setState({
            editLoading : false,
            employees : employees,
            modalActionData : {},
            editResponse : {
                errors : result.success ? false : true,
                success: result.success ? true : false
            },
            employeeCount: this.state.employeeCount - 1
        });
    }

}

export default HRDashboardStore;
