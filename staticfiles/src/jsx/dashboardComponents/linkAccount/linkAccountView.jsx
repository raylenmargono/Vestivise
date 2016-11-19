import React from 'react';
import NavBar from '../navBar.jsx';
import {NavBarConst} from "../const/navBar.const";
import API from '../../../js/api';

const style = {
    iframeStyle : {
        "height" : "100%",
        "width" : "100%"
    }
}

const test = ".button{background-color:#ee6e73}"

class LinkAccountView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'LinkAccountView';
        this.state = {
            quovoIframeUrl : "",
            error: false
        }
    }


    componentDidMount(){
        API.get(Urls.quovoLinkUrl())
            .done(function(payload){
                this.setState({
                   quovoIframeUrl : payload.data.iframe_url
                });
            }.bind(this))
            .error(function(e){
                this.setState({
                    error : true
                });
            }.bind(this))
    }

    render() {
        return (
            <div>
                <NavBar
                    navbarConst={NavBarConst.LINK_ACCOUNT}
                />
                <iframe style={style.iframeStyle} src={this.state.quovoIframeUrl}></iframe>
            </div>
        );
    }
}

export default LinkAccountView;
