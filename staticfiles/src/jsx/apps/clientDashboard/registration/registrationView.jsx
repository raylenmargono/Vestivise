import React, {Component} from 'react';
import API from 'js/api';
import NProgress from 'nprogress';

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
            userState : ""
        }
    }

    componentDidUpdate(){
        if(this.state.error){
             Materialize.showStaggeredList('#staggered-list');
        }
    }

    componentDidMount(){
        $('select').material_select();
        $(this.refs.state).material_select(this.handleStateChange.bind(this));
        $('.select-dropdown').val("State");
        $('.select-dropdown').css('color', '#9A9A9D');
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
        payload['state'] = this.state.userState;
        payload['setUpUserID'] = this.props.setUpUserID;

        var error = false;
        var inputs = [];
        var messages = [];

        if(!payload.state){
            error = true;
            inputs = ["state"];
            messages = ["State is required"]
        }

        else if(payload.password != payload.password2){
            error = true
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
                    error = true;
                    if("error" in error.response.body){
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
                            window.location.href = Urls.dashboard();
                        }
                        else{
                            messages.push("An internal error occurred. Contact support@vestivise.com.");
                        }
                    });
                }
            }.bind(this));

        }
    }

    getInputClass(name, isHalf, isLeft){
        var base = "valign center-block input-field";
        if(isHalf){
            base += " col m6 ";
            base += isLeft ? "half-input-left" : "half-input-right";
        }
        else{
            base += " col m5 s8";
        }
        return this.state.handlers.inputs.includes(name) ? base + " error" : base;
    }


    handleStateChange(){

        $('.select-dropdown').css('color', 'black');
        this.setState({
            userState : this.refs.state.value
        });
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

    render(){
        return(
        <div className="container">
            <ul id="staggered-list">
                {this.getErrorMessages()}
            </ul>
            <div className="row">
                <div className="col s12">
                    <div className="row valign-wrapper">
                        <img id="logo" className="valign center-block" src={'/media/logoSmall.png'} alt="Vestivise" />
                    </div>
                </div>
            </div>
            <div className="valign-wrapper">
                <div className="valign center-block max-width">
                    <form ref="form" onSubmit={this.register.bind(this)}>
                        <div className="row">
                            <div className="col m12">
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("username")}>
                                        <input ref="username" placeholder="Username" id="username" name="username" type="text" required/>
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
                            </div>
                        </div>
                        <div className="row">
                            <div className="col m12">
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("")}>
                                        <div className={this.getInputClass("firstName", true, true)}>
                                            <input ref="name" placeholder="First Name" id="firstName" name="firstName" type="text" required/>
                                        </div>
                                        <div className={this.getInputClass("lastName", true, false)}>
                                            <input ref="name" placeholder="Last Name" id="lastName" name="lastName" type="text" required/>
                                        </div>
                                    </div>
                                </div>
                                <div className="row valign-wrapper input-row-g1">
                                    <div className={this.getInputClass("birthday")}>
                                        <input ref="birthday" placeholder="Birthday (YYYY/MM/DD)" id="birthday" name="birthday" type="text" required/>
                                    </div>
                                </div>
                                <div className="row valign-wrapper input-row-g1">
                                    <div style={{"marginTop" : 0}} className={this.getInputClass("")}>
                                        <div className={this.getInputClass("state", true, true)}>
                                            <select ref="state" required>
                                                <option value="AL">Alabama</option>
                                                <option value="AK">Alaska</option>
                                                <option value="AZ">Arizona</option>
                                                <option value="AR">Arkansas</option>
                                                <option value="CA">California</option>
                                                <option value="CO">Colorado</option>
                                                <option value="CT">Connecticut</option>
                                                <option value="DE">Delaware</option>
                                                <option value="DC">District Of Columbia</option>
                                                <option value="FL">Florida</option>
                                                <option value="GA">Georgia</option>
                                                <option value="HI">Hawaii</option>
                                                <option value="ID">Idaho</option>
                                                <option value="IL">Illinois</option>
                                                <option value="IN">Indiana</option>
                                                <option value="IA">Iowa</option>
                                                <option value="KS">Kansas</option>
                                                <option value="KY">Kentucky</option>
                                                <option value="LA">Louisiana</option>
                                                <option value="ME">Maine</option>
                                                <option value="MD">Maryland</option>
                                                <option value="MA">Massachusetts</option>
                                                <option value="MI">Michigan</option>
                                                <option value="MN">Minnesota</option>
                                                <option value="MS">Mississippi</option>
                                                <option value="MO">Missouri</option>
                                                <option value="MT">Montana</option>
                                                <option value="NE">Nebraska</option>
                                                <option value="NV">Nevada</option>
                                                <option value="NH">New Hampshire</option>
                                                <option value="NJ">New Jersey</option>
                                                <option value="NM">New Mexico</option>
                                                <option value="NY">New York</option>
                                                <option value="NC">North Carolina</option>
                                                <option value="ND">North Dakota</option>
                                                <option value="OH">Ohio</option>
                                                <option value="OK">Oklahoma</option>
                                                <option value="OR">Oregon</option>
                                                <option value="PA">Pennsylvania</option>
                                                <option value="RI">Rhode Island</option>
                                                <option value="SC">South Carolina</option>
                                                <option value="SD">South Dakota</option>
                                                <option value="TN">Tennessee</option>
                                                <option value="TX">Texas</option>
                                                <option value="UT">Utah</option>
                                                <option value="VT">Vermont</option>
                                                <option value="VA">Virginia</option>
                                                <option value="WA">Washington</option>
                                                <option value="WV">West Virginia</option>
                                                <option value="WI">Wisconsin</option>
                                                <option value="WY">Wyoming</option>
                                            </select>
                                        </div>
                                        <div className={this.getInputClass("zipCode", true, false)}>
                                            <input ref="zipCode" placeholder="Zipcode" id="zipCode" name="zipCode" type="text" required/>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="row valign-wrapper input-row">
                            <div className="input-field col m5 s8 valign center-block">
                                <button type="submit" className="waves-effect btn valign center-block max-width">Submit</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
            <p id="morning-star">© 2016 Morningstar. All Rights Reserved. The information contained herein: (1) is proprietary to Morningstar and/ or its content providers; (2) may not be copied or distributed; and (3) is not warranted to be accurate, complete or timely. Neither Morningstar nor its content providers are responsible for any damages or losses arising from any use of this information. Past performance is no guarantee of future results.</p>
            <a id="login-here" href={Urls.loginPage()}><strong>Have an account?</strong> Login here <img src={'/media/icon-arrow-right-white.svg'} className="arrow"/></a>
        </div>
        );
    }

}


export default RegistrationView;