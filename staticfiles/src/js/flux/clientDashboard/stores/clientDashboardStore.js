/**
 * Created by raylenmargono on 12/6/16.
 */
import {DataSource} from 'js/flux/clientDashboard/sources/sources';
import {ClientDataAction, ClientAppAction} from 'js/flux/clientDashboard/actions/actions';
import { datasource, bind, createStore } from 'alt-utils/lib/decorators';
import alt from 'js/flux/alt';
import ModuleStack from './ModuleStack';
import Module from './Module';
import {Storage} from 'js/utils';

class DashboardStore{

    constructor(moduleAPI){
        this.moduleAPI = moduleAPI;
    }

    getState(){
        return {
            isLoading: false,
            profileFetchError : false,
            moduleFetchError : false,
            user: {},
            isCompleted : false,
            isLinked : false,
            notifications : {},
            moduleStacks : {
                Asset : new ModuleStack("Asset"),
                Return : new ModuleStack("Return"),
                Risk: new ModuleStack("Risk"),
                Cost : new ModuleStack("Cost"),
                Other : new ModuleStack("Other")
            },
            accounts : [],
            navElement : null,
            didFetch : false
        };
    }

    bindAppListeners(){
        this.bindListeners({
            loadingResults : ClientDataAction.loadingResults,
            recievedProfileResults : ClientDataAction.recievedProfileResults,
            fetchingProfileResultsFailed : ClientDataAction.fetchingProfileResultsFailed,
            recievedModuleResults : ClientDataAction.recievedModuleResults,
            fetchingModuleResultsFailed : ClientDataAction.fetchingModuleResultsFailed,
            nextModule : ClientAppAction.nextModule,
            prevModule : ClientAppAction.prevModule,
            renderNewNavEl : ClientAppAction.renderNewNavElement,
            refetchModuleData : ClientDataAction.refetchModuleData
        });
    }

    renderNewNavEl(el){
        this.setState({
            navElement : el
        });
    }

    nextModule(category){
        const moduleStacks = this.state.moduleStacks;
        const stack = moduleStacks[category];
        stack.next();
        this.setState({
           moduleStacks : moduleStacks
        });
    }

    prevModule(category){
        const moduleStacks = this.state.moduleStacks;
        const stack = moduleStacks[category];
        stack.prev();
        this.setState({
           moduleStacks : moduleStacks
        });
    }

    loadingResults(){
        this.setState({
            isLoading: true
        });
    }

    recievedProfileResults(data, isReFetch){
        const result = data['data'];

        var moduleStacks = this.state.moduleStacks;

        if(!this.state.didFetch){
            result["modules"].forEach(function(moduleRequest){
                const category = moduleRequest["category"];
                const moduleName = moduleRequest["name"];
                const moduleEndpoint = moduleRequest["endpoint"];
                const moduleID = moduleRequest["moduleID"];

                const module = new Module(moduleName, moduleEndpoint, category, moduleID);
                const stack = moduleStacks[category];
                stack.pushModule(module);
            });
        }

        this.setState({
            user : {
                firstName : result["firstName"],
                lastName : result["lastName"],
                company : result["company"]
            },
            isCompleted : result["isCompleted"],
            isLinked : result["isLinked"],
            notifications : result["notification"],
            moduleStacks : moduleStacks,
            isLoading : result["isCompleted"] && result["isLinked"] ? true : false,
            accounts : result["accounts"],
            didFetch : true
        });
        if(result["isCompleted"] && result["isLinked"]){
            for(var key in moduleStacks){
                const list = moduleStacks[key].getList();
                list.forEach(function(module){
                    ClientDataAction.fetchModule(module, this.moduleAPI, []);
                }.bind(this))
            }
        }
    }

    refetchModuleData(filters){
        if(this.state.isCompleted && this.state.isLinked){
            for(var key in this.state.moduleStacks){
                const module = this.state.moduleStacks[key];
                const list = module.getList();
                module.restartPendingData();
                list.forEach(function(module){
                    ClientDataAction.fetchModule(module, this.moduleAPI, filters);
                }.bind(this))
            }
        }
    }

    fetchingProfileResultsFailed(data){
        this.setState({
           profileFetchError: true
        });
    }

    recievedModuleResults(payload){
        const data = payload["data"];
        const module = payload["module"];
        this.handleModuleRequest(data, module);
    }

    fetchingModuleResultsFailed(payload){
        const module = payload["module"];
        this.handleModuleRequest({data : null}, module);
    }

    handleModuleRequest(data, module){
        var moduleStacks = this.state.moduleStacks;
        const stack = moduleStacks[module.getCategory()];
        stack.updateData(module, data);
        moduleStacks[module.getCategory()] = stack;
        var isLoading = false;
        for(var key in moduleStacks){
            var m = moduleStacks[key];
            console.log(m.type + " " + m.pendingData);
            if(m.pendingData != 0) isLoading = true;
        }
        console.log(isLoading);
        this.setState({
            moduleStacks : moduleStacks,
            isLoading : isLoading
        });
    }

}

@datasource(DataSource)
class DemoDashboardStore extends DashboardStore{
    constructor(){
        super(Urls.demoData);
        this.state = this.getState();
        this.state["profileAPIURL"] = Urls.demoProfile;
        this.state["isDemo"] = true;

        this.bindAppListeners();
    }
}

@datasource(DataSource)
class ClientDashboardStore extends DashboardStore{
    constructor(){
        super(Urls.broker);
        this.state = this.getState();
        this.state["profileAPIURL"] = Urls.profile;
        this.state["isDemo"] = false;

        this.bindAppListeners();
    }
}

export {ClientDashboardStore, DemoDashboardStore};
