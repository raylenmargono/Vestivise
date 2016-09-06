import React from 'react';
import API from '../../js/api';

const headerStyle = {
	"color" : "#F34258", 
	"textAlign" : "center",
	"marginBottom" : "30"
}

class SalesLeadModal extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'SalesLeadModal';
    }

    componentDidMount() {
         if(this.props.isDemo){
			$('#salesLeadModal').openModal({
				dismissible: false, // Modal can be dismissed by clicking outside of the modal
				opacity: 0.8,
			});
         } 
    }

    salesLeadSubmit(e){

    	e.preventDefault();

    	const payload = {
    		fullName : this.refs.fullName.value,
    		company : this.refs.company.value,
    		email : this.refs.email.value
    	};

    	API.post(Urls.subscribeToSalesList(), payload)
    	.done(function(res){
    		console.log(res);
    	})
    	.fail(function(e){
    		console.log(e);
    	})
    	.always(function(){
    		$('#salesLeadModal').closeModal();
    	});
    }

    render() {
        return (

        	<div id='salesLeadModal' className="modal">
				<div className="modal-content">
					<h5 style={headerStyle}>Please enter you contact info below to view the demo.</h5>
					<form onSubmit={this.salesLeadSubmit.bind(this)}>
						<div className="input-field col m12">
							<i className="material-icons prefix">perm_identity</i>
							<input required aria-required="true" ref='fullName' id="fullName" type="text" className="validate" />
	          				<label htmlFor="fullName">Full Name</label>
          				</div>			

						<div className="input-field col m12">
	          				<i className="material-icons prefix">language</i>
							<input required aria-required="true" ref='company' id="company" type="text" className="validate" />
	          				<label htmlFor="company">Company</label>		
						</div>

						<div className="input-field col m12">
							<i className="material-icons prefix">email</i>
							<input required aria-required="true" ref='email' id="email" type="email" className="validate" />
	          				<label htmlFor="email">Email</label>	
	          			</div>

          				<button className="btn waves-effect waves-light" type="submit">Submit
    						<i className="material-icons right">send</i>
  						</button>
					</form>
				</div>
			
			</div>
        	
        );
    }
}

export default SalesLeadModal;
