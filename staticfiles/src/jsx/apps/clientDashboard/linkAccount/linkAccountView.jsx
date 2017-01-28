import React, {Component} from 'react';
import API from 'js/api';
import MainViewWalkThrough from 'js/walkthrough/mainViewWalkThrough';
import {Storage} from 'js/utils';

const style = {
    iframe : {
        "width" : "100%",
        "flex" : "1",
        "border" : 0
    },
    appContainer : {
        "display" : "flex",
        "flexDirection" : "column",
        "minHeight" : "100vh"
    },
    nav : {
        "backgroundColor" : "#F43E54",
    },
    logo: {
        "height": "64px",
        "marginLeft" : "20px"
    },
    dashboardbutton: {
        "backgroundColor" : "#00B7FA",
    },
}

class LinkAccountView extends Component{

    constructor(props){
        super(props);
        this.state = {
            widget_frame : ""
        }
    }

    componentDidMount() {
        API.get(Urls.quovoLinkUrl())
        .end(function(err, res){
            if(!err){
                this.setState({
                   widget_frame : res.body.data.iframe_url
                });
            }
        }.bind(this));
        $( document ).ready(function(){
            $(".button-collapse").sideNav();
        });
        var w = Storage.get("walkthroughProgress");
        if(!w["linkage"]){
            MainViewWalkThrough.startWalkThrough("linkage");
            w["linkage"] = true;
            Storage.put(w);
        }

    }

    render(){
        return(
            <div style={style.appContainer}>
                <nav style={style.test}>
                    <div style={style.nav} className="nav-wrapper">
                        <a href={Urls.dashboard()} ><img src={'/media/logo.png'} style={style.logo}></img></a>
                        <a href="#" data-activates="mobile-demo" className="button-collapse"><i className="material-icons">menu</i></a>
                        <ul className="right hide-on-med-and-down">
                            <li><a id="returnButton" className="waves-effect waves-light btn-large" style={style.dashboardbutton} href={Urls.dashboard()}>Return To Dashboard</a></li>
                        </ul>
                        <ul className="side-nav" id="mobile">
                            <li><a className="waves-effect waves-light btn-large" style={style.dashboardbutton} href={Urls.dashboard()}>Return To Dashboard</a></li>
                        </ul>
                    </div>
                </nav>
                <iframe style={style.iframe} src={this.state.widget_frame}></iframe>
            </div>
        );
    }

}


export default LinkAccountView;