import React, {Component} from 'react';
import API from 'js/api';

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
        "backgroundColor" : "#F43E54"
    },
    logo: {
        "height": "64px",
        "margin-left" : "20px"
    },
    dashboardbutton: {
        "backgroundColor" : "#00B7FA"
    }
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
    }

    render(){
        return(
            <div style={style.appContainer}>
                <nav>
                    <div style={style.nav} className="nav-wrapper">
                        <a href={Urls.dashboard()} ><img src={'/media/logo.png'} style={style.logo}></img></a>
                        <ul  className="right hide-on-med-and-down">
                            <li><a style={style.dashboardbutton} className="waves-effect waves-light btn" href={Urls.dashboard()}>Return To Dashboard</a></li>
                        </ul>
                    </div>
                </nav>
                <iframe style={style.iframe} src={this.state.widget_frame}></iframe>
            </div>
        );
    }

}


export default LinkAccountView;