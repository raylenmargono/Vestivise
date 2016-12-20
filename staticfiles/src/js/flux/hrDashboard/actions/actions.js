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

}

@createActions(alt)
class EmployeeEditAction{

}

export {EmployeeSearchAction, EmployeeEditAction};

