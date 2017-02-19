/**
 * Created by raylenmargono on 12/6/16.
 */
import alt from 'js/flux/alt';
import { createActions } from 'alt-utils/lib/decorators';
import {ModuleSource, DataSource} from 'js/flux/clientDashboard/sources/sources';

@createActions(alt)
class ClientDataAction{

    fetchModule(module, api, filters){
        console.warn = function(){};
        const endpoint = module.getEndpoint();
        ModuleSource.fetch(api, endpoint, filters)
        .end(function(err, res){
            if(err){
                this.fetchingModuleResultsFailed(err, module);
            }
            else{
                this.recievedModuleResults(res.body, module);
            }
        }.bind(this));
    }

    refetchProfile(){
        console.warn = function(){};
        DataSource.getProfileFetch.remote({
            profileAPIURL : Urls.profile
        })
        .end(function(err, res){
           if(err){
               DataSource.getProfileFetch.error(err);
           }
           else{
               DataSource.getProfileFetch.success(res);
           }
        });
    }

    loadingResults(){
        return true;
    }

    recievedProfileResults(data){
        return data.body;
    }

    fetchingProfileResultsFailed(data){
        return data.body;
    }

    recievedModuleResults(data, module){
        return {
            data: data,
            module: module
        };
    }

    fetchingModuleResultsFailed(data, module){
        return {
            data: data,
            module: module
        };
    }

    refetchModuleData(filters){
        return filters;
    }

}

@createActions(alt)
class ClientAppAction{

    handleHideNav(scroll_top){
        return scroll_top > 30;
    }

    nextModule(category){
        return category;
    }

    prevModule(category){
        return category;
    }

    renderNewNavElement(el){
        return el;
    }
}

export {ClientAppAction, ClientDataAction}