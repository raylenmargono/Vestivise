import React, {Component} from 'react';
import NProgress from 'nprogress';
import API from 'js/api';

class ProfileView extends Component{

    constructor(props){
        super(props);
        NProgress.configure({ showSpinner: false });
        this.state = {
            editMode : false,
            username : GLOBAL.username,
            errMsg : ""
        }
    }

    toggleState(){
        this.setState({
            editMode : !this.state.editMode
        });
    }

    updateProfile(e){
        e.preventDefault();
        NProgress.start();
        console.log(e.target);
        const email = e.target.email.value;
        const password1 = e.target.password1.value;
        const password2 = e.target.password2.value;

        if(password1 != password2 && (password1 || password2)){
            NProgress.done();
            NProgress.remove();
            this.setState({
                errMsg : "Password do not match"
            });
            return;
        }

        const payload = {
            email : email,
            password : password1
        }

        API.put(Urls.profileUpdate(), payload)
            .end(function(err, res){
                NProgress.done();
                NProgress.remove();
                if(err && err.status != 200){
                    if("error" in err.response.body){
                        var errorObj = err.response.body.error;
                        var message = errorObj['password'];
                        if(!message && errorObj['username']){
                            message = errorObj['username']
                        }
                        this.setState({
                            errMsg : message
                        });
                    }
                    else{
                        this.setState({
                            errMsg : "An internal error occurred. Contact support@vestivise.com."
                        });
                    }
                }
                else{
                    this.toggleState();
                    this.setState({
                        errMsg : "",
                        username : email
                    });
                }
            }.bind(this));

    }

    render(){
        return (
            <div id="pv-container">
                <div className="row">
                    <div className="col m12">
                        <h5 id="welcome-header">Welcome {GLOBAL.name}</h5>
                    </div>
                </div>
                <form onSubmit={this.updateProfile.bind(this)}>
                    <div className="row valign-wrapper">
                        <div className="input-field col m5 s8 valign center-block ">
                            <input defaultValue={this.state.username} ref="email" placeholder="Email" name="email" type="email" required/>
                        </div>
                    </div>
                    <div className="row valign-wrapper">
                        <div className="input-field col m5 s8 valign center-block ">
                            <input ref="password1" placeholder="New Password" name="password1" type="password"/>
                        </div>
                    </div>
                    <div className="row valign-wrapper">
                        <div className="input-field col m5 s8 valign center-block ">
                            <input ref="password2" placeholder="Re-Enter Password" name="password2" type="password"/>
                        </div>
                    </div>
                    <div className="row valign-wrapper input-row">
                        <div className="input-field col m5 s8 valign center-block">
                            <button
                                type="submit"
                                className="waves-effect btn valign center-block max-width"
                            >
                                Finish Changes
                            </button>
                            <p id="errMsg">{this.state.errMsg}</p>
                        </div>
                    </div>
                </form>
            </div>
        );
    }

}


export default ProfileView;