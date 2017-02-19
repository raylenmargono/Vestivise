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
            return(
                <div id="navigation">
                    <a href={Urls.signUpPage()} >Contact</a>
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
                <a id="logo" href="/">
                    <img src={"/media/logo-symbol.png"} />
                </a>
                {this.getOptions()}
            </div>
        );
    }

}


export default FloatingNav;