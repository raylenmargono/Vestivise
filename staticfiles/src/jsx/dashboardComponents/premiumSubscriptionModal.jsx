import React from 'react';
import API from '../../js/api';

class PremiumSubscriptionModal extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'PremiumSubscriptionModal';
    }

    getTitle(){
    	if(this.props.currentModalInformation == "insights"){
    		return "Vestivise Premium - Insights";
    	}
    	return "Vestivise Premium - Comparisons";
    }

    getContent(){
    	if(this.props.currentModalInformation == "insights"){
    		return (
    			<div>
	    			<p>With Vestivise Premium comes deeper insights into your investments.</p>
	    			<p>Over time the vestivise team will be coming up with new insights to better improve your report.</p> 

	    			<ul>
	    				<li><h5 className='premiumOfferingsHead'>Assets</h5></li>
	    				<li className="divider"></li>
	    				<li><p>Stock Sector</p></li>
	    				<li><p>Stock Cap</p></li>
	    				<li><p>Bond Type</p></li>
	    				<li><p>Other Breakdowns</p></li>
	    				
	    				<li><h5 className='premiumOfferingsHead'>Returns</h5></li>
	    				<li className="divider"></li>
	    				<li><p>Sort by dollar or percentage</p></li>
	    				<li><p>Determine contributions and withdrawals</p></li>
	    				<li><p>Learn more about market historicals</p></li>
	    				
	    				<li><h5 className='premiumOfferingsHead'>Risk</h5></li>
	    				<li className="divider"></li>
	    				<li><p>Risk Category</p></li>
	    				<li><p>Determine High Risk Areas</p></li>
	    				<li><p>Lower Your Risk</p></li>
	    				
	    				<li><h5 className='premiumOfferingsHead'>Costs</h5></li>
	    				<li className="divider"></li>
	    				<li><p>Tax Treatment</p></li>
	    				<li><p>Inflation</p></li>
	    				<li><p>Specific Fund Costs</p></li>
	    			</ul>
	    		</div>
    		);
    	}

    	return (
				<div>
	    			<p>With Vestivise Premium comes deeper insights into your investments.</p>
	    			<p>Over time the vestivise team will be coming up with new insights to better improve your report.</p> 
	    			<h5 className="premiumOfferingsHead">Don't go in it alone!</h5>
	    			<li className="divider"></li>
	    			<p>
	    				With Vestivise Premium comes user comparions for 
	    				your whole report. Using your specific investment data 
	    				and the Vestivise user base as a whole, 
	    				we generate comparisons for each category of 
	    				information: assets, returns, risks, and costs. 
	    				You can be compared by various demographic types: age, risk profiles, income, and others.
	    			</p>
	    		
				</div>
    	);
    }

    subscribe(e){

    	e.preventDefault();
    	const fName = this.refs.firstName.value;
    	const lName = this.refs.lastName.value;
    	const email = this.refs.email.value;

    	const mailingListPayload = {
			email : email,
			firstName : fName,
			lastName : lName
		};

    	API.post(Urls['email-list'](), mailingListPayload)
    	.done(function(res){
    		console.log(res);
    	})
    	.fail(function(e){
    		console.log(e);
    	})
    	.always(function(){
    		$('#informationModal').closeModal();
    	});

    }

    render() {
        return (
        	<div id="informationModal" className="modal modal-fixed-footer">
                <div className="modal-content">
                  <h4 id='premiumPromoHead'>{this.getTitle()}</h4>
                  <li className="divider"></li>
                  {this.getContent()}
                </div>
                <div className="modal-footer">
                  <a className=" modal-action modal-close waves-effect waves-green btn-flat">Close</a>
                </div>
            </div>
        );
    }
}

export default PremiumSubscriptionModal;
