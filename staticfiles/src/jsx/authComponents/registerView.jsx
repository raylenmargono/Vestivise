import React from 'react';
const API = require('../../js/api.js');

class RegisterView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'RegisterView';

        var date = new Date();

        this.state = {
        	birthday : date.getFullYear() + "-" + date.getMonth() + "-" + date.getDate(),
        	userState : "",
        	error : null,
        	loading: false
        } 
    }

    componentDidMount() {
    	$(document).ready(function() {
    		$('select').material_select();
    		$('.datepicker').pickadate({
				selectMonths: true, // Creates a dropdown to control month
				selectYears: 150, // Creates a dropdown of 15 years to control year
				format: 'yyyy-mm-dd'
			});
			//$('#birthday').val("1990-01-01");
		});     
    }

    register(e){

    	e.preventDefault();

    	this.setState({
    		error : null,
    		loading: true
    	});

    	const username = this.refs.username.value;
    	const password = this.refs.password.value;
    	const email = this.refs.email.value;
    	const firstName = this.refs.firstName.value;
    	const lastName = this.refs.lastName.value;
    	const income = this.refs.income.value;

    	const birthday = this.refs.birthday.value;
    	const state = this.refs.state.value;

    	const payload = {
    		'username' : username,
    		'password' : password,
    		'email' : email,
    		'firstName' : firstName,
    		'lastName' : lastName,
    		'birthday' : birthday,
    		'state' : state,
    		'income' : income
    	} 

    	API.post(Urls.register(), payload)
    	.done(function(res){
    		console.log('user registered');
    		API.post(Urls.login(), {'username' : username, 'password' : password})
    		.done(function(res){
    			window.location.href = Urls.dashboard();
    		})
    		.fail(function(e){
    			this.setState({
    				error: e
    			})
    			console.log(e);
    		}.bind(this))
    		.always(function(){
    			this.setState({
    				loading: false
    			});
    		}.bind(this))
    	})
    	.fail(function(e){
    		console.log(e.responseJSON.error);
			this.setState({
			 	error : e.responseJSON.error
			});
    	}.bind(this))
    	.always(function(){
    		this.setState({
    			loading: false
    		});
    	}.bind(this));

    }
    setBirthday(event, date){
    	this.setState({
    		birthday : date.getFullYear() + "-" + date.getMonth() + "-" + date.getDate()
    	})
    }
    handleError(type){
    	var error = this.state.error;
    	if(error && type in error){
    		return error[type];
    	}
    	return "";
    }

    getMinDate(){
    	var date = new Date();
    	date.setFullYear(date.getFullYear() - 200);
    	return date;

    }

    getLoader(){
    	return this.state.loading ? 
    			(
	    			<div className="progress">
	      				<div className="indeterminate"></div>
	  				</div>
  				) : null;
    }

    render() {

        return( 
        	<div className='container'>
        		<div className='cardContainer'>
        			<div className='row'>
                        <div className='col m12'>
                            <img id='logo' src="../../static/media/logo.jpg" />
                        </div>
                    </div>
					<div className='row'>
                        <div className='col m12'>
                            <div className='card'>
								<form onSubmit={this.register.bind(this)}>
									
									<div className="card-content">
                                        <p className="card-title">Register</p>
                                        <div className='row'>
                                            <div className="input-field col s12">
                                                <input ref='username' id="username" type="text" className={this.handleError('username') ? "invalid" : ""} required/>
                                                <label data-error={this.handleError('username')} htmlFor="username">Username</label>
                                            </div>
                                        </div>
                                        <div className='row inputRow'>  
                                            <div className="input-field col s12">
                                                <input ref='password' id="password" type="password" className={this.handleError('password') ? "invalid" : ""} required/>
                                                <label data-error={this.handleError('password')} htmlFor="password">Password</label>
                                            </div>
                                        </div>
                                        <div className='row inputRow'>  
                                            <div className="input-field col s12">
                                                <input ref='email' id="email" type="email" className={this.handleError('email') ? "invalid" : ""} required/>
                                                <label data-error={this.handleError('email')} htmlFor="email">Email</label>
                                            </div>
                                        </div>
                                        <div className='row inputRow'>  
                                            <div className="input-field col s6">
                                                <input ref='firstName' id="firstName" type="text" className={this.handleError('firstName') ? "invalid" : ""} required/>
                                                <label data-error={this.handleError('firstName')} htmlFor="firstName">First Name</label>
                                            </div>
                                            <div className="input-field col s6">
                                                <input ref='lastName' id="lastName" type="text" className={this.handleError('lastName') ? "invalid" : ""} required/>
                                                <label data-error={this.handleError('lastName')} htmlFor="lastName">Last Name</label>
                                            </div>
                                        </div>
                                        <div className='row inputRow'>  
                                            <div className="input-field col s4">
                                                <input ref='income' id="income" type="text" className={this.handleError('income') ? "invalid" : ""} required/>
                                                <label data-error={this.handleError('income')} htmlFor="income">Income</label>
                                            </div>
                                            <div className="input-field col s4">
                                                <label data-error={this.handleError('birthday')} htmlFor="birthday">Birthday</label>
                                                <input defaultValue={"1995-01-01"} ref='birthday' id="birthday" type="date" className={this.handleError('birthday') ? "invalid datepicker" : "datepicker"} required/>
                                            </div>
                                            <div className="input-field col s4">
											    <select id='state' defaultValue={"AL"} ref='state'>
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
												<label htmlFor="state">State</label>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="card-action">

	                                    <button 
										    className='waves-effect waves-light btn'
										    type='submit'
										    >
										    Register
										</button>

										<a 
										    href={Urls.loginPage()} 
										    className='waves-effect waves-light btn-flat black-text'
										    >
										    Already Signed Up? Login
										</a>
                                        
                                        
                                        {this.getLoader()}
                                    </div>

								</form>
							</div>
						</div>
					</div>
				</div>
			</div>
        )
    }
}



export default RegisterView;
