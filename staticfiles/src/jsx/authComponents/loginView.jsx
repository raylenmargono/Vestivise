import React from 'react';
import API from '../../js/api.js';
import { getParameterByName, getRootUrl } from '../../js/utils.js';

const style = {
	inputStyle : {
		"fontSize" : "20px"
	},
	actionStyle : {
		'marginTop' : "20px"
	}
}


class LoginView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'LoginView';

        this.state = {
        	error : "",
            isLoading : false
        }
    }

    login(e){

    	e.preventDefault();

        this.setState({
            isLoading : true
        });

    	const username = this.refs.username.value;
    	const password = this.refs.password.value;

    	const payload = {
    		'username' : username,
    		'password' : password
    	};

    	API.post(Urls.login(), payload)
    	.done(function(res){
    		if(getParameterByName('next')){
    			window.location.href = getRootUrl() + getParameterByName('next');
    		}else{
    			window.location.href = Urls.dashboard();
    		}
    	}.bind(this))
    	.fail(function(error){
    		this.setState({
    			error : error.responseJSON.error
    		})
    	}.bind(this))
        .always(function(){
            this.setState({
                isLoading : false
            });
        }.bind(this));
    }

    getLoader(){
        if(this.state.isLoading){
            return (
                <div className="progress">
                    <div className="indeterminate"></div>
                </div>
            );
        }
        return null;
    }

    getCardTitle(){
    	if(getParameterByName('next')){
    		return "Please re-enter your username and password";
    	}else{
    		return "Login";
    	}
    }

    getRegisterButton(){
    	if(!getParameterByName('next')){
    		return (
                <a href={Urls.signUpPage()} className='waves-effect waves-light btn-flat black-text'>New? Register</a>
    		);
    	}
    	else{
    		return null;
    	}
    }

    render() {
        return(

            <div className="container">

                <div id="cardContainer">
                    <div className='row'>
                        <div className='col m12'>
                            <img id='logo' src="../../static/media/logo.jpg" />
                        </div>
                    </div>
                    <div className='row'>
                        <div className='col m12'>
                            <div className='card'>
                                <form onSubmit={this.login.bind(this)}>
                                    <div className="card-content">
                                        <p className="card-title">{this.getCardTitle()}</p>
                                        <div className='row'>
                                            <div className="input-field col s12">
                                                <input ref='username' id="username" type="text" className={this.state.error ? "invalid" : ""} required/>
                                                <label data-error={this.state.error} htmlFor="username">Username</label>
                                            </div>
                                        </div>
                                        <div className='row'>  
                                            <div className="input-field col s12">
                                                <input ref='password' id="password" type="password" className={this.state.error ? "invalid" : ""} required/>
                                                <label data-error={this.state.error} htmlFor="password">Password</label>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="card-action">
                                        <button 
                                            type='submit' 
                                            className='waves-effect waves-light btn'
                                            >
                                            Login
                                        </button>
                                        {this.getRegisterButton()}
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

export default LoginView;
