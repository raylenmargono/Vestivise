import React, {Component} from 'react';

class DetailResponseView extends Component{

    constructor(props){
        super(props);
    }

    render(){
        var success = this.props.editResponse.success ? "Success" : "Failure";
        return(
            <div className="row">
              <div className="col m12">
                  <h5 className="request-info">{success}</h5>
              </div>
          </div>
        );
    }

}


export default DetailResponseView;