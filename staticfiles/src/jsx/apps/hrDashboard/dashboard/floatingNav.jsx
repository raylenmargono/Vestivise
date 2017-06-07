import React, {Component} from 'react';

class FloatingNav extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div id="header">
                <div id="logo">
                    <img src={'/media/logo-symbol.png'} />
                </div>
                <div id="navigation">
                    <a href="mailto:support@vestivise.com">Support</a>
                    <a href={Urls.logoutAdmin()} id="nav-logout">Logout</a>
                </div>
            </div>
        );
    }

}


export default FloatingNav;