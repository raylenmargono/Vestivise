import React, {Component} from 'react';

class FloatingNav extends Component{

    constructor(props){
        super(props);

    }

    componentDidMount(){
        if(!this.props.isDemo){
            $('select').material_select();
        }
    }

    openAccountModal(){
        $('#accountModal').modal("open");
    }

    openHoldingModal(){
        $('#holdingModal').modal("open");
    }

    getOptions(){
        if(this.props.isDemo){

            function trackEvent(){
                 fbq('track', 'Lead');
            }

            return(
                <div id="navigation">
                    <a onClick={trackEvent} href={Urls.signUpPage()} >Free Sign Up</a>
                </div>
            );
        }
        return (
            <div id="navigation">
                <a id="filterButton" onClick={this.openAccountModal}>Accounts</a>
                <a id="holdingButton" onClick={this.openHoldingModal}>Holdings</a>
                <a id="filterButton" href={Urls.settingsPage()}>Settings</a>
                <a href="mailto:support@vestivise.com">Support</a>
                <a href={Urls.logout()} >Logout</a>
            </div>
        );
    }

    render(){
        return(
            <div id="header">
                <a href="#" disabled tabIndex="-1" id="logo">
                    <img src={"/media/logo-symbol.png"} />
                </a>
                {this.getOptions()}
            </div>
        );
    }

}


export default FloatingNav;