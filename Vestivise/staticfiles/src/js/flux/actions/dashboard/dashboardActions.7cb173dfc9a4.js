import alt from '../../alt';

class AppActions{


	dataLoading(){
		return true;
	}

	dataSuccess(data){
		return data;
	}

	dataFail(error){
		return error;
	}

	nextModuleInStack(module){
		return module;
	}

	animate(stack, moduleID , moduleName, topRowHeight){
		return {
			stack : stack,
			moduleName : moduleName,
			topRowHeight : topRowHeight,
			moduleID : moduleID
		}
	}

}

export default alt.createActions(AppActions);