import React, {Component} from 'react';
import NProgress from 'nprogress';
import API from 'js/api';

class PasswordRecoveryView extends Component{

    constructor(props){
        super(props);
        NProgress.configure({ showSpinner: false });
        this.state = {
            sentLink : false,
            resetPassword: false,
            resetPasswordError : ""
        }
    }

    recoveryPassword(e){
        e.preventDefault();
        NProgress.start();
        const email = e.target.email.value
        const payload = {
            "email" : email
        };
        API.post(Urls.passwordRecovery(), payload)
            .end(function(err, res){
                NProgress.done();
                NProgress.remove();
                this.setState({
                    sentLink : true
                });
            }.bind(this));
    }

    resetPassword(e){
        e.preventDefault();
        NProgress.start();
        const password1 = e.target.password1.value;
        const password2 = e.target.password2.value;

        if(password1 != password2){
            NProgress.done();
            NProgress.remove();
            this.setState({
                resetPasswordError : "Passwords do not match",
                resetPassword : false
            });
            return;
        }

        const payload = {
            "linkID" : this.props.linkID,
            "password" : password1
        };
        API.post(Urls.passwordReset(), payload)
            .end(function(err, res){
                NProgress.done();
                NProgress.remove();
                if(err && err.status != 200){
                    if("error" in err.response.body){
                        var errorObj = err.response.body.error;
                        var message = errorObj['password'];
                        this.setState({
                            resetPassword : false,
                            resetPasswordError : message
                        });
                    }else{
                        this.setState({
                            resetPasswordError : "An internal error occurred. Contact support@vestivise.com.",
                            resetPassword : false
                        });
                    }
                }
                else{
                    this.setState({
                        resetPassword : true,
                        resetPasswordError : ""
                    });
                }
            }.bind(this));
    }

    getResetMessage(){
        if(!this.state.resetPassword && !this.state.resetPasswordError){
            return "";
        }
        if(this.state.resetPassword){
            return "Successfully Reset Password";
        }
        else{
            return this.state.resetPasswordError;
        }
    }

    getContainer(){
        if(!this.props.linkID){
            return(
                <form onSubmit={this.recoveryPassword.bind(this)}>
                    <div className="row valign-wrapper input-row-text">
                        <div className="input-field col m5 s8 valign center-block">
                            <input ref="email" placeholder="What's your email?" id="recovery-link-input" name="email" type="email" required/>
                        </div>
                    </div>
                    <div className="row valign-wrapper input-row">
                        <div className="input-field col m5 s8 valign center-block">
                            <button type="submit" className="waves-effect btn valign center-block max-width">Send Recovery Link</button>
                            {this.state.sentLink ? <p id="recovery-link-message">Recovery Link Sent</p> : null}
                        </div>
                    </div>
                </form>
            );
        }
        return(
            <form onSubmit={this.resetPassword.bind(this)}>
                <div className="row valign-wrapper input-row-text">
                    <div className={"input-field col m5 s8 valign center-block " + (this.state.resetPasswordError ? "error" : "")}>
                        <input ref="password1" placeholder="Password" name="password1" type="password" required/>
                    </div>
                </div>
                <div className="row valign-wrapper input-row-text">
                    <div className={"input-field col m5 s8 valign center-block " + (this.state.resetPasswordError ? "error" : "")}>
                        <input ref="password2" placeholder="Re-Enter Password" name="password2" type="password" required/>
                    </div>
                </div>
                <div className="row valign-wrapper input-row">
                    <div className="input-field col m5 s8 valign center-block">
                        <button type="submit" className="waves-effect btn valign center-block max-width">Reset Password</button>
                        <p id="recovery-link-message">{this.getResetMessage()}</p>
                    </div>
                </div>
            </form>
        );
    }

    render(){
        return(
            <div className="container">
                <div>
                    <div className="row">
                        <div className="col s12">
                            <div className="row valign-wrapper">
                                <img id="logo" className="valign center-block" src="/media/logoSmall.png" alt="Vestivise" />
                            </div>
                        </div>
                    </div>
                    <div className="valign-wrapper">
                        <div className="valign center-block max-width">
                            {this.getContainer()}
                        </div>
                    </div>
                </div>
            </div>
        );
    }

}


export default PasswordRecoveryView;