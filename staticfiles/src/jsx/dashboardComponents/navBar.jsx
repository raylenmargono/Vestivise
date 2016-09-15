import React from 'react';
import { NavBarConst } from './const/navBar.const';
import { StackConst } from '../../js/const/stack.const';

class NavBar extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'NavBar';
    }

    getActive(navbarConst, navItem){
    	if(navbarConst == navItem){
    		return "active"; 
    	}
    	return "";
    }

    showOptions(){
    	if(!this.props.isDemo){
    		return(
	    		<div>
		    		<ul id="nav-mobile" className="left hide-on-med-and-down nav-bar-left">
						<li 
							id="linkAccountButton"
						>
							<a href={Urls.linkAccount()}>Link Accounts</a>
						</li>
						<li 
							id="linkAccountButton"
						>
							<a href={Urls.updateDataPage()}>Update Dashboard</a>
						</li>
					</ul>
					<ul id="nav-mobile" className="right hide-on-med-and-down nav-bar-right">
						<li 
							id="optionsButton"
							className={this.getActive(this.props.navbarConst, "OPTIONS")}
						>
							<a href={Urls.optionsPage()}>Options</a>
						</li>
						<li 
							id="logoutButton"
						>
							<a href={Urls.logout()}>Logout</a>
						</li>
					</ul>
				</div>
			);
    	}
    	return null;
    }

    render() {
        return (
        	<div>
	        	<nav>
					<div className="nav-wrapper vestBar">
						<a href={Urls.dashboard()} className="brand-logo center">
							<img id='vestivise-nav-logo' src="./../static/media/logo.jpg" alt="" />
						</a>
						{this.showOptions()}
					</div>
				</nav>
			</div>
        );
    }
}

export default NavBar;
