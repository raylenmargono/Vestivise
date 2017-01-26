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

    getOptions(){
        if(this.props.isDemo){
            return(
                <div id="navigation">
                    <a href="mailto:sales@vestivise.com" >Contact</a>
                </div>
            );
        }
        return (
            <div id="navigation">
                <a onClick={this.openAccountModal}>Accounts</a>
                <a href={Urls.linkAccountPage()}>Settings</a>
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