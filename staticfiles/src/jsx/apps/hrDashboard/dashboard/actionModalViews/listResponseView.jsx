import React, {Component} from 'react';

class ListResponseView extends Component{

    constructor(props){
        super(props);
    }

    render(){
        var response = this.props.editResponse;
        if("internalError" in response){
            return(
              <div>
                  <h5>Internal Error</h5>
                  <p>{response.errorMessage}</p>
              </div>
            );
        }
        var errors = response.errors.length;
        var success = response.success.length;
        return (
            <div>
                <div className="row">
                    <div className="col m2">
                        <h5 className="request-info">{success}</h5>
                    </div>
                <div className="col m6">
                    <p>Requests sent</p>
                </div>
                </div>
                <div className="row">
                    <div className="col m2">
                        <h5 className="request-info">{errors}</h5>
                    </div>
                    <div className="col m6">
                        <p>Requests failed</p>
                        <p className="grey-text small">Employee is already added or you entered an invalid email</p>
                    </div>
                </div>
            </div>
        );
    }

}


export default ListResponseView;