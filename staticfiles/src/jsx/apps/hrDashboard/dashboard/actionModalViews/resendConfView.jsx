import React, {Component} from 'react';
import DetailResponseView from './detailResponseView.jsx';

class ResendConfView extends Component{

    constructor(props){
        super(props);
        this.state = {
            incorrect : false
        }
    }

    resendConf(e){
        e.preventDefault();
        if(this.props.modalActionData.email != this.refs.email.value){
            this.setState({
               incorrect : true
            });
        }
        else{
            this.props.editAction.resendUserConfirmationLink(this.props.modalActionData);
        }
    }

    render(){
        if(!this.props.editResponse) {
            return (
                <form onSubmit={this.resendConf.bind(this)}>
                    <div className="row valign-wrapper input-row-text">
                        <div className={"input-field col m10 valign center-block" + (this.state.incorrect ? " error" : "")}>
                            <input ref="email" placeholder="Email" id="email" name="email" type="email"
                                   required/>
                            <p className="grey-text small">{this.props.modalActionData.email}</p>
                        </div>
                    </div>
                    <div className="row valign-wrapper input-row">
                        <div className="input-field col m10 valign center-block">
                            <button type="submit" className="waves-effect btn valign center-block max-width">Submit
                            </button>
                        </div>
                    </div>
                </form>
            );
        }
        return <DetailResponseView editResponse={this.props.editResponse}/>;
    }

}


export default ResendConfView;