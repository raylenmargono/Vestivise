import alt from '../../alt';
import { StackConst } from '../../../const/stack.const';
import AppActions from '../../actions/dashboard/dashboardActions';
import { DashboardSource } from '../../sources/dashboard/dashboardSource';
import API from '../../../api';
import Stack from "./stack";
import Animation from "../../../animation/dashboard.js";

class DashboardStore{

	constructor(){
		this.bindListeners({
			nextModuleInStack : AppActions.nextModuleInStack,
			loadDashboard : AppActions.dataLoading,
			loadBasicAccountData : AppActions.dataSuccess,
            animate : AppActions.animate,
            loadBasicAccountData : AppActions.loadFakeData,
	    });

	    this.state = {
	    	riskStack : new Stack(),
	    	returnStack : new Stack(),
	    	costStack : new Stack(),
	    	assetStack : new Stack(),
	    	isLoading : false,
            hasLinkedAccount : false,
            isProcessing: false
	    };

	    this.registerAsync(DashboardSource);
	    
	}

	onSearch() {
		if (!this.getInstance().isLoading()) {
			this.getInstance().performSearch();
		}
	}

	loadDashboard(){
    	this.setState({
    		isLoading : true
  		});
	}

    loadBasicAccountData(data){

        this.setState({
            isLoading : false,
            hasLinkedAccount: data.linkedAccount,
            isProcessing : data.processing
        });

    	var riskStack = this.state.riskStack;

    	var returnStack = this.state.returnStack;

    	var costStack = this.state.costStack;

    	var assetStack = this.state.assetStack;

        console.log("test");

        if(!data.linkedAccount || data.processing){
            return;
        }

        for(var i = 0 ; i < data.account_modules.length ; i++){
            const module = data.account_modules[i].module;
            switch(module.category){
                case StackConst.RISK:
                    riskStack.pushModule(module);
                    break;
                case StackConst.ASSET:
                    assetStack.pushModule(module);
                    break;
                case StackConst.RETURN:
                    returnStack.pushModule(module);
                    break;
                case StackConst.COST:
                    costStack.pushModule(module);
                    break;
            }
        }
    	
    	this.setState({
    		riskStack :  riskStack,
    		performanceStack : returnStack,
    		costStack : costStack,
    		assetStack : assetStack 
    	});

    }

    animate(payload){

        const stack = payload.stack;
        const module = payload.moduleName;
        const moduleID = payload.moduleID;
        const topRowHeight = payload.topRowHeight;
        var isFullScreen = this.state.isFullScreen;

        if(this.state.isAnimating){
            return;
        }

        var handleAnimation = function(){
            this.setState({
                isAnimating : !this.state.isAnimating,
                currentModule : module
            });
        }.bind(this);

        handleAnimation();

        this.setState({
            isFullScreen : !isFullScreen
        });

        var animationFunction = null;

        switch(stack){
            case StackConst.RISK:
                animationFunction = Animation.animateRisk;
                break;
            case StackConst.RETURN:
                animationFunction = Animation.animateReturn;
                break;
            case StackConst.ASSET:
                animationFunction = Animation.animateAssets;
                break;
            case StackConst.COST:
                animationFunction = Animation.animateCost;
                break;
        }

        animationFunction(
            moduleID,
            isFullScreen,
            topRowHeight,
            handleAnimation.bind(this)
        );
    }

    nextModuleInStack(stack){
    	var state;
    	var stack;
    	switch(stack){
    		case StackConst.RISK:
    			stack = this.state.riskStack;
    			stack.next();
    			state = { riskStack : stack};
    			break;
    		case StackConst.RETURN:
    			stack = this.state.returnStack;
    			stack.next();
    			state = { returnStack : stack};
    			break;
    		case StackConst.ASSET:
    			stack = this.state.assetStack;
    			stack.next();
    			state = { assetStack : stack };
    			break;
    		case StackConst.Cost:
    			stack = this.state.costStack;
    			stack.next();
    			state = { costStack : stack };
    			break;
    	}

    	this.setState(state);
    }

}

export default alt.createStore(DashboardStore, 'DashboardStore');
