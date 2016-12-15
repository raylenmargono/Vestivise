import React, {Component} from 'react';

class ModuleDescription extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div className="row">
                <div className="col m4">
                    <h5>{this.props.title}</h5>
                    <p className="grey-text"></p>
                </div>
            </div>
        );
    }

}


export default ModuleDescription;