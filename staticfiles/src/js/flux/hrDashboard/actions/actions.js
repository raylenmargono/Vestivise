/**
 * Created by raylenmargono on 12/6/16.
 */
import alt from 'js/flux/alt';
import { createActions } from 'alt-utils/lib/decorators';
import {EmployeeSource, HRProfileSource} from 'js/flux/hrDashboard/sources/sources';
import API from 'js/api';

@createActions(alt)
class EmployeeSearchAction{

    paginate(index, query){
        console.warn = function(){}
        this.loadingResults();
        EmployeeSource.performSearch.remote(null, index, query)
        .end(function(err, res){
            if(err){
                this.fetchingResultsFailed(err);
            }
            else{
                this.receivedResults({
                    data : res.body,
                    query : query,
                    page : index
                });
            }
        }.bind(this));
    }

    search(query){
        console.warn = function(){}
        this.loadingResults();
        EmployeeSource.performSearch.remote(null, 1, query)
        .end(function(err, res){
            if(err){
                this.fetchingResultsFailed(err);
            }
            else{
                this.receivedResults({
                    data : res.body,
                    query : query,
                    page : 1
                });
            }
        }.bind(this));
    }

    loadingResults(){
        return true;
    }

    receivedResults(data){
        return data;
    }

    fetchingResultsFailed(data){
        return data;
    }

}

@createActions(alt)
class EmployeeEditAction{

    createUserWithCSV(file){
        var formData = new FormData();
        formData.append('csv_file', file);
        API.post(Urls.employeeCreateCSV(), formData)
        .end(function(err, res){
            if(err){

            }else{

            }
        });
    }

}

@createActions(alt)
class HRProfileActions{

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

export {EmployeeSearchAction, EmployeeEditAction, HRProfileActions};

