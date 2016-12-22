import React, {Component} from 'react';
import logoSymbol from 'media/logo-symbol.png';

class FloatingNav extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div id="header">
                <a id="logo" href="/">
                    <img src={logoSymbol} />
                </a>
                <div id="navigation">
                    <a href="">Support</a>
                    <a href="" id="nav-logout">Logout</a>
                </div>
            </div>
        );
    }

}


export default FloatingNav;