/**
 * Created by raylenmargono on 12/6/16.
 */
import alt from 'js/flux/alt';
import { createActions } from 'alt-utils/lib/decorators';
import {ModuleSource, DataSource, TrackingSource} from 'js/flux/clientDashboard/sources/sources';

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

@createActions(alt)
class TrackingAction{

    trackAction(trackID, data){
        console.warn = function(){};
        const payload = {
            track_info : {
                track_id: trackID,
                track_data : data
            }
        };
        TrackingSource.post(payload)
        .end(function(err, res){});
    }

    startShepardTimer(){
        return true;
    }

    stopShepardTimer(){
        return true;
    }

    trackDashboardInformation(moduleStacks){
        var list = [];
        for(var key in moduleStacks){
            var stack = moduleStacks[key].getList();
            for(var i in stack){
                var module = stack[i];
                list.push({
                    id : module.mID,
                    time : module.timeOnScreen
                });
            }
        }
        return list;
    }

    dashboardShown(didShow){
        console.warn = function(){};
        this.trackAction("dashboard_data_shown", didShow);
    }
}

export {ClientAppAction, ClientDataAction, TrackingAction};