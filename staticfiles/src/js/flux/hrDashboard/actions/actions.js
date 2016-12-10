/**
 * Created by raylenmargono on 12/6/16.
 */
import alt from 'js/flux/alt';
import { createActions } from 'alt-utils/lib/decorators';

@createActions(alt)
class EmployeeSearchAction{

    fetch(query, page){
        return {
            searchQuery : query,
            page : page
        }
    }

    loadingResults(){
        return true;
    }

    receivedResults(data){
        return data.body;
    }

    fetchingResultsFailed(data){
        return data.body;
    }

    handleHideNav(scroll_top){
        return scroll_top > 30;
    }
}

@createActions(alt)
class EmployeeEditAction{

}

@createActions(alt)
class HRAppAction{

    handleHideNav(scroll_top){
        return scroll_top > 30;
    }

}

export const employeeSearchAction = EmployeeSearchAction;
export const employeeEditAction = EmployeeEditAction;
export const hrAppAction = HRAppAction;

