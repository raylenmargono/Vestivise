import React, {Component} from 'react';
import API from 'js/api';
import NProgress from 'nprogress';
import {isMobile} from 'js/utils';

class LoginPage extends Component{

    constructor(props) {
        super(props);
        NProgress.configure({ showSpinner: false });
        this.state = {
            error : false
        }
    }

    auth(e){
        NProgress.start();
        e.preventDefault();
        const payload = {
            "username" : e.target.username.value,
            "password" : e.target.password.value
        };
        API.post(this.props.method, payload)
            .end(function(err, res){
                NProgress.done();
                NProgress.remove();
                if(err){
                    this.setState({
                        error : true
                    });
                }
                else{
                    window.location.href = this.props.dashboardUrl;
                }
            }.bind(this));
    }

    getInputClass(){
        var base = "input-field col m5 s8 valign center-block";
        if(isMobile()){
            base = "input-field col m12 s8 valign center-block";
        }
        return this.state.error ? base + " error" : base;
    }

    getErrorMessage(){
        return this.state.error ? <p id="login-error-message">Either your email or password is incorrect</p> : null;
    }

    getLogo(){
        if(isMobile()){
            return '/media/logo.png';
        }
        return '/media/logoSmall.png';
    }

    render(){
        return(
            <div className="container">
                <div className="row">
                    <div className="col s12">
                        <div className="row valign-wrapper">
                            <img id="logo" className="valign center-block" src={this.getLogo()} alt="Vestivise" />
                        </div>
                    </div>
                </div>
                <div className="valign-wrapper">
                    <div className="valign center-block max-width">
                        <form onSubmit={this.auth.bind(this)}>
                            <div className="row valign-wrapper input-row-text">
                                <div className={this.getInputClass()}>
                                    <input ref="username" placeholder="Email" id="username" name="username" type="email" required/>
                                </div>
                            </div>
                            <div className="row valign-wrapper input-row-text">
                                <div className={this.getInputClass()}>
                                    <input ref="password" placeholder="Password" id="password" name="password" type="password" required/>
                                </div>
                            </div>
                            <div className="row valign-wrapper input-row">
                                <div className={this.getInputClass()}>
                                    {this.getErrorMessage()}
                                    <button type="submit" className="waves-effect btn valign center-block max-width">Login</button>
                                    <a href={Urls.passwordRecoveryPage()} id="forgotPasswordLink">Forgot Password? Recover Your Account</a>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
                <a id="sign-up-here" href={Urls.loginPage()}><strong>Don't have an account?</strong> Sign up here <img src={'/media/icon-arrow-right-white.svg'} className="arrow"/></a>
            </div>
        );
    }

}


export default LoginPage;