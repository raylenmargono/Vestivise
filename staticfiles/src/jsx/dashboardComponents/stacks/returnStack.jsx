import React from 'react';
import ModuleFactory from '../factories/moduleFactory.jsx';
import AppActions from '../../../js/flux/actions/dashboard/dashboardActions';
import { StackConst } from '../../../js/const/stack.const';

class ReturnStack extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'ReturnStack';
    }

    getCurrentModule(){
        const stack = this.props.data;
        const currentModule = stack.getCurrentModule();

        if(currentModule){
            const name = currentModule.getModuleID();
            var endpoint = currentModule.getEndPoint();

            if(this.props.isDemo){
                endpoint  = endpoint + "Test";
            }
            return ModuleFactory.createModule(name, endpoint);
        }
        return null;
    }

    animate(){

        const stack = this.props.data;
        const currentModule = stack.getCurrentModule();
        AppActions.animate(StackConst.RETURN, currentModule.getModuleID(), currentModule.getName(), null);
    }

    render() {
        return (
        	<div onClick={this.animate.bind(this)}>
				{this.getCurrentModule()}
				<p className="modTitle L">Returns</p>
			</div>
        );
    }
}

export default ReturnStack;
