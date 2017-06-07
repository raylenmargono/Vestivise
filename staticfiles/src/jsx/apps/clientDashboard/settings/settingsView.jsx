import React, {Component} from 'react';
import MainViewWalkThrough from 'js/walkthrough/mainViewWalkThrough';
import {Storage} from 'js/utils';
import LinkAccountView from './linkAccountView.jsx';
import ProfileView from './profileView.jsx';

class SettingsView extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount() {

        $(document).ready(function(){
            $('ul.tabs').tabs();
        });
        var w = Storage.get("walkthroughProgress");
        if(!w["linkage"]){
            MainViewWalkThrough.startWalkThrough("linkage", null);
            w["linkage"] = true;
            Storage.put("walkthroughProgress", w);
        }

    }

    render(){
        return(
            <div>
                <nav>
                    <div id="nav" className="nav-wrapper">
                        <a href={Urls.dashboard()} ><img src={'/media/logo.png'} id="logo"></img></a>
                        <ul className="right">
                            <li><a id="returnButton" className="waves-effect waves-light btn-large" href={Urls.dashboard()}>Return To Dashboard</a></li>
                        </ul>
                    </div>
                </nav>
                <div id="viewContainer" className="row">
                    <div id="appContainer" className="col s12">
                        <ul style={{"overflowX": "hidden"}} className="tabs tabs-fixed-width">
                            <li className="tab col s3"><a href="#la">Link Accounts</a></li>
                            <li className="tab col s3"><a href="#pv">Profile</a></li>
                        </ul>
                        <div>
                            <div id="la" className="col s12 view"><LinkAccountView /></div>
                            <div id="pv" className="col s12 view"><ProfileView /></div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

}


export default SettingsView;