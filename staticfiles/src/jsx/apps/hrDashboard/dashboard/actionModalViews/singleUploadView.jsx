import React, {Component} from 'react';
import ListResponseView from './listResponseView.jsx';

class SingleUploadView extends Component{

    constructor(props){
        super(props);
    }

    oneEmployeeAdd(e){
        e.preventDefault();
        const email = this.refs.newUserEmailInput.value;
        this.props.editAction.createUserWithEmail(email);
    }

    render(){
        if(!this.props.editResponse){
            return (
                <form onSubmit={this.oneEmployeeAdd.bind(this)}>
                    <div className="row valign-wrapper input-row-text">
                        <div className="input-field col m10 valign center-block">
                            <input ref="newUserEmailInput" placeholder="Email" id="email" name="email" type="email" required/>
                            <p className="grey-text small">Login info and instructions will be sent to the users email.</p>
                        </div>
                    </div>
                    <div className="row valign-wrapper input-row">
                        <div className="input-field col m10 valign center-block">
                            <button type="submit" className="waves-effect btn valign center-block max-width">Submit</button>
                        </div>
                    </div>
                </form>
            );
        }
        return <ListResponseView editResponse={this.props.editResponse}/>;

    }

}


export default SingleUploadView;