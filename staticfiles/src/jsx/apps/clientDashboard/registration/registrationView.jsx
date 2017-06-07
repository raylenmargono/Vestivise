import React, {Component} from 'react';
import API from 'js/api';
import NProgress from 'nprogress';
import {isMobile} from 'js/utils';

class RegistrationView extends Component{

    constructor(props){
        super(props);
        NProgress.configure({ showSpinner: false });
        this.state = {
            error : false,
            handlers: {
                inputs : [],
                messages : []
            },
            didSelectTerms: false,
            birthday: ""
        }
    }

    componentDidUpdate(){
        if(this.state.error){
             Materialize.showStaggeredList('#staggered-list');
        }
    }

    register(event){
        NProgress.start();

        function setError(parent, error, inputs, messages){
            NProgress.done();
            NProgress.remove();
            parent.setState({
                error : error,
                handlers : {
                    inputs : inputs,
                    messages : messages
                }
            });
        }

        event.preventDefault();
        const data = $(this.refs.form).serializeArray();
        var payload = {};
        for(var i in data){
            var item = data[i];
            payload[item.name] = item.value;
        }
        payload['setUpUserID'] = this.props.setUpUserID;

        var error = false;
        var inputs = [];
        var messages = [];

        if(payload.password != payload.password2){
            error = true;
            inputs = ["password", "password2"];
            messages = ["Password does not match"];
        }

        if(error){
            setError(this, error, inputs, messages);
        }

        else{
            API.post(Urls.register(), payload)
            .end(function(err, res){
                if(err && err.status != 200){
                    NProgress.done();
                    NProgress.remove();
                    error = true;
                    if("error" in err.response.body){
                        var errorObj = err.response.body.error;
                        for(var key in errorObj){
                            inputs.push(key);
                            messages.push(errorObj[key]);
                        }
                    }else{
                        messages.push("An internal error occurred. Contact support@vestivise.com.");
                    }
                    setError(this, error, inputs, messages);
                }
                else{
                    API.post(Urls.login(), payload)
                    .end(function(err, res){
                        NProgress.done();
                        NProgress.remove();
                        if(!err){
                            try{
                                fbq('track', 'CompleteRegistration');
                                goog_report_conversion(Urls.dashboard());
                            }
                            catch(err){
                                window.location.href = Urls.dashboard();
                            }
                        }
                        else{
                            messages.push("An internal error occurred. Contact support@vestivise.com.");
                        }
                    });
                }
            }.bind(this));

        }
    }

    getInputClass(name, isHalf, isLeft) {
        var base = "valign center-block input-field";
        if (isHalf) {
            base += " col m6 ";
            base += isLeft ? "half-input-left" : "half-input-right";
        }
        else if(isMobile()) {
            base += " col m12 s8";
        }
        else{
            base += " col m5 s8";
        }
        return this.state.handlers.inputs.includes(name) ? base + " error" : base;
    }

    getErrorMessages(){

        if(!this.state.error) return null;

        var result = [];

        result.push(
            <li key={-1}>
                <h4 key={-1}>Incomplete Form</h4>
            </li>
        );

        for(var i in this.state.handlers.messages){
            result.push(
                <li key={i}>
                    <p key={i}>{this.state.handlers.messages[i]}</p>
                </li>
            );
        }
        return result;
    }

    getActionable(){

        function acceptTerms() {
            setTimeout(function () {
                this.setState({
                   didSelectTerms : true
                });
            }.bind(this), 300);
        }
        const buttonHidden = this.state.didSelectTerms ? "" : "hide";
        const toaHidden = this.state.didSelectTerms ? "hide" : "";

        return(
            <div>
                <button type="submit" className={"waves-effect btn valign center-block max-width " + buttonHidden}>Submit</button>
                <div className={toaHidden}>
                    <input onChange={acceptTerms.bind(this)} name="termsConditions" type="checkbox" id="termsConditions" required/>
                    <label htmlFor="termsConditions">
                        <a target="_blank" id="termsConditions-link" href="http://www.vestivise.com/terms">
                            I have read this Agreement and agree to the terms and conditions
                        </a>
                    </label>
                </div>
            </div>
        );
    }

    getActionClass(){
        if(isMobile()){
            return "input-field col m12 s8 valign center-block";
        }
        return "input-field col m5 s8 valign center-block";

    }

    onKeyDown(e) {
        if (e.keyCode === 8) {
            this.setState({
                birthday : this.state.birthday.substr(0, this.state.birthday.length - 1)
            });
        }
    }

    processBirthday(event){
        var value = event.target.value;
        value = value.replace(/\//g, "");
        if(value.match(/\D/g)) return;
        var first = value.substr(0,2);
        var second = value.substr(2,2);
        var last = value.substr(4,4);
        if(first.length == 2){
            first += "/";
        }
        if(second.length == 2) {
            second += "/";
        }
        this.setState({
            birthday : first + second + last
        });
    }


    render(){
        return(
        <div className="container">
            <div id="logo-row" className="row">
                <div className="col s12">
                    <div className="row valign-wrapper">
                        <img id="logo" className="valign center-block" src={'/media/logo.png'} alt="Vestivise" />
                    </div>
                </div>
            </div>
            <div className="row">
                <div className="col s12">
                    <ul id="staggered-list">
                        {this.getErrorMessages()}
                    </ul>
                </div>
            </div>
            <div className="valign-wrapper">
                <div className="valign center-block max-width">
                    <form ref="form" onSubmit={this.register.bind(this)}>
                        <div className="row">
                            <div className="col m12">
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("username")}>
                                        <input defaultValue={this.props.email} ref="username" placeholder="Email" id="username" name="username" type="email" required/>
                                    </div>
                                </div>
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("password")}>
                                        <input ref="password" placeholder="Password" id="password" name="password" type="password" required/>
                                    </div>
                                </div>
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("password")}>
                                        <input ref="password2" placeholder="Confirm Password" id="password2" name="password2" type="password" required/>
                                    </div>
                                </div>
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("birthday")}>
                                        <input
                                            value={this.state.birthday}
                                            onChange={this.processBirthday.bind(this)}
                                            ref="birthday"
                                            placeholder="Birthday (MM/DD/YYYY)"
                                            id="birthday"
                                            name="birthday"
                                            type="text"
                                            onKeyDown={this.onKeyDown.bind(this)}
                                            required
                                        />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="row valign-wrapper input-row">
                            <div className={this.getActionClass()}>
                                {this.getActionable()}
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <p id="morning-star">© 2016 Morningstar. All Rights Reserved. The information contained herein: (1) is proprietary to Morningstar and/ or its content providers; (2) may not be copied or distributed; and (3) is not warranted to be accurate, complete or timely. Neither Morningstar nor its content providers are responsible for any damages or losses arising from any use of this information. Past performance is no guarantee of future results.</p>
            <a id="login-here" href={Urls.loginPage()}><strong>Have an account?</strong> Login here <img src={'/media/icon-arrow-right-white.svg'} className="arrow"/></a>
            <a id="learn-more" href="https://www.vestivise.com"><strong>Want to learn more?</strong> Visit Website <img src={'/media/icon-arrow-right-white.svg'} className="arrow"/></a>
        </div>
        );
    }

}


export default RegistrationView;