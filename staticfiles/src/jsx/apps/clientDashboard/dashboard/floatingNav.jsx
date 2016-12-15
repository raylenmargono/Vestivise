import React, {Component} from 'react';
import logoSymbol from 'media/logo-symbol.png';

class FloatingNav extends Component{

    constructor(props){
        super(props);
    }

    getOptions(){
        if(this.props.isDemo){
            return(
                <div id="navigation">
                    <a href="" id="nav-logout">Contact</a>
                </div>
            );
        }
        return (
            <div id="navigation">
                <a href="">Settings</a>
                <a href="">Support</a>
                <a href="" id="nav-logout">Logout</a>
            </div>
        );
    }

    render(){
        return(
            <div id="header">
                <a id="logo" href="/">
                    <img src={logoSymbol} />
                </a>
                {this.getOptions()}
            </div>
        );
    }

}


export default FloatingNav;