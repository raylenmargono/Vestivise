/**
 * Created by raylenmargono on 12/6/16.
 */
import alt from 'js/flux/alt';
import { createActions } from 'alt-utils/lib/decorators';
import {EmployeeSource, HRProfileSource} from 'js/flux/hrDashboard/sources/sources';
import API from 'js/api';
import NProgress from 'nprogress';

@createActions(alt)
class EmployeeSearchAction{

    paginate(index, query){
        NProgress.start();
        console.warn = function(){}
        this.loadingResults();
        EmployeeSource.performSearch.remote(null, index, query)
        .end(function(err, res){
            NProgress.done();
            NProgress.remove();
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
        NProgress.start();
        console.warn = function(){}
        this.loadingResults();
        EmployeeSource.performSearch.remote(null, 1, query)
        .end(function(err, res){
            NProgress.done();
            NProgress.remove();
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

    selectUserForEdit(id){
        return id;
    }

    deleteUser(payload){
        this.loadingResults();
        NProgress.start();
        API.delete(Urls["companyEmployeeManagement-detail"](payload.id))
        .end(function(err, res){
            NProgress.done();
            NProgress.remove();
            if(err){
                this.deleteUserResponse(false, payload.trueIndex);
            }
            else{
                this.deleteUserResponse(true, payload.trueIndex);
            }
        }.bind(this));
    }

    resendUserConfirmationLink(payload){
        this.loadingResults();
        NProgress.start();
        var payload = {
            'setupUserID' : payload.id
        }
        API.post(Urls.reinviteUser(), payload)
        .end(function(err, res){
            NProgress.done();
            NProgress.remove();
            if(err){
                this.sendLinkResponse(false);
            }
            else{
                this.sendLinkResponse(true);
            }
        }.bind(this));
    }

    createUserWithCSV(file){
        this.loadingResults();
        NProgress.start();
        var formData = new FormData();
        formData.append('csv_file', file);
        API.post(Urls.employeeCreateCSV(), formData)
        .end(function(err, res){
            NProgress.done();
            NProgress.remove();
            if(err){
                this.fetchingResultsFailed(err, false);
            }else{
                this.receivedResults(res, false);
            }
        }.bind(this));
    }

    createUserWithEmail(email){
        this.loadingResults();
        NProgress.start();
        var payload = {
            "email" : email
        }
        API.post(Urls['companyEmployeeManagement-list'](), payload)
        .end(function(err, res){
            NProgress.done();
            NProgress.remove();
            if(err){
                this.fetchingResultsFailed(err, true);
            }else{
                this.receivedResults(res, true);
            }
        }.bind(this));
    }

    resetEditState(){
        return true;
    }

    loadingResults(){
        return true;
    }

    sendLinkResponse(result){
        return result;
    }

    deleteUserResponse(result, index){
        console.log(result);
        return {
            success: result,
            index : index
        }
    }

    receivedResults(data, isSingle){
        var temp =  data.body;
        var result = {
            success : [],
            errors : []
        }
        if(isSingle){
            result["success"] = [temp.data];
        }
        else{
            result["success"] = temp.data.success;
            result["errors"] = temp.data.errors;
        }

        return result;
    }

    fetchingResultsFailed(err, isSingle){
        var res = err.response.body;
        var result = {
            errors : []
        };
        if(isSingle && "data" in res){
            result["singleFail"] = true;
            result["errors"] = [res["data"]];
        }
        return result;
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

