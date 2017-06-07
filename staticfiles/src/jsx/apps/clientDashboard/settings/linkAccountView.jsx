import React, {Component} from 'react';
import API from 'js/api';

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
            <iframe id="iframe" src={this.state.widget_frame}></iframe>
        );
    }

}


export default LinkAccountView;