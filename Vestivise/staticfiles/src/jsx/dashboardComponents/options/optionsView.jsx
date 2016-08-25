import React from 'react';
import API from '../../../js/api';
import NavBar from '../navBar.jsx';
import { NavBarConst } from '../const/navBar.const';

class OptionsView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'OptionsView';

        this.state = {
        	accounts : [],
        	currentUnlinkSelection : -1
        };
    }

    componentDidMount() {
    	this.handleAccountRetrieval();     
    	$('.modal-trigger').leanModal();
    }

    handleAccountRetrieval(){
    	API.get(Urls.linkedAccountsList())
    	.done(function(accounts){
    		this.setState({
    			accounts : accounts
    		});
    	}.bind(this))
    	.fail(function(e){
    		console.log(e);
    	})
    }

    selectUnlink(index){
    	$('#modalAlert').openModal();
    	this.setState({
    		currentUnlinkSelection : index
    	});
    }

    getAccounts(){

    	var index = -1;

    	return this.state.accounts.map(function (account) {
    		return (

    			<li key={index++}>
					<div className="collapsible-header">
						<div className='row'>
							<div className='col m6'>
								<p className="accountTypeLabel">
									{account.container.toUpperCase()}
								</p>
						 	</div>
						 	<div className='col m6'>
						 		<p>{account.accountName}</p>
						 	</div>
						</div>
					</div>
		      		<div className="collapsible-body">

		      			<div className='row'>

		      				<div className='col m3 offset-m1'>
		      					<button 
									className="modal-trigger waves-effect waves-teal btn unlinkButton"
									onClick={this.selectUnlink.bind(this, index)}
								>
									Unlink
								</button>
		      				</div>

		      				<div className='col m8'>
		      					<p>Remove Account From Dashboard</p>
		      				</div>

		      			</div>
		      			
		      		</div>
	      		</li>
    		);
    	}.bind(this));
    }

    enterEditMode(){

    	this.setState({
    		editMode : !this.state.editMode
    	});

    }

    getAccountModule(){
    	return (
			<div className='col m6'>
				<div className="card-panel white">
					<div className='card-content'>
    				    <h5 className="card-title teal-text">Linked Accounts</h5>
    				    <ul className='collapsible popout' data-collapsible="accordion">
							{this.getAccounts()}
						</ul>
					</div>
		        </div>
			</div>
    	);
    }

    getSupportModule(){
    	return (
    		<div className='col m6'>
    			<div className="card-panel white">
					<div className='card-content'>
    				    <h5 className="card-title teal-text">Support</h5>
    				    <div id='supportContainer' className='row'>
    				    	<div className='col m2'>
    				    		<a 
    				    			className="btn-floating btn-large waves-effect waves-light red"
    				    			href='mailto:support@vestivise.com'
    				    		>
		    				    	<i className="material-icons">email</i>
		    				    </a>
    				    	</div>
    				    	<div className='col m9'>
    				    	    <p>Something Not Working? Send Us A Message!</p>
    				    	</div>
    				    </div>
					</div>
		        </div>
        	</div>
    	);
    }

    unlinkAccount(){
    	const index = this.state.currentUnlinkSelection;
        var accounts = this.state.accounts;
        const account = accounts[index];
        API.delete(Urls.linkedAccountsDetail(account.accountID))
        .done(function(response){
            if (index > -1) {
                accounts.splice(index, 1);
            }

            this.setState({
                accounts: accounts
            });

            $('#modalAlert').closeModal();
            $(".collapsible-header").removeClass(function(){
                return "active";
            });
            $(".collapsible").collapsible({accordion: true});
            $(".collapsible").collapsible({accordion: false});
        }.bind(this))
        .fail(function(e){
            const rt = e.responseText;
            if("detail" in  JSON.parse(rt) && "error_code" in JSON.parse(JSON.parse(rt)["detail"])){
                const code = JSON.parse(JSON.parse(rt)["detail"])["error_code"];
                if(code == "Y1"){
                    window.location.href = Urls.loginPage() + "?next=" +  Urls.optionsPage();
                }
            }
        });
        
    }

    render() {
        return (
            <div>
                <NavBar 
                    navbarConst={NavBarConst.OPTIONS}
                />
            	<div className='container'>
            	    <div id='contentContainer' className='row'>
    	        		{this.getAccountModule()}
    	        		{this.getSupportModule()}
    	        	</div>
    	        	<div id="modalAlert" className="modal">
    					<div className="modal-content">
    						<h4 className='text-teal'>Unlink Account</h4>
    						<p>Are you sure?</p>
    					</div>	
    					<div className="modal-footer">
    						<button 
    							className=" modal-action waves-effect waves-green btn-flat"
    							onClick={this.unlinkAccount.bind(this)}
    						>
    							Agree
    						</button>
    						<button 
    							className=" modal-action modal-close waves-effect waves-green btn-flat"
    						>
    							Cancel
    						</button>
    					</div>
    				</div>
            	</div>
            </div>
        );
    }
}

export default OptionsView;
