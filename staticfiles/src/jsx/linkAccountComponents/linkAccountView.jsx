import React from 'react';
import API from '../../js/api.js';
import { getRootUrl } from '../../js/utils.js';

const account = {
	username: "sbMemvestivise1",
    password: "sbMemvestivise1#123"
}


class LinkAccountView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'LinkAccountView';
    }

    componentWillMount() {
        window.loading_screen = window.pleaseWait({
            logo: "../../static/media/logo.jpg",
            backgroundColor: '#F24258',
            loadingHtml: "<div class='sk-cube-grid'>"
                        +"<div class='sk-cube sk-cube1'></div>"
                        +"<div class='sk-cube sk-cube2'></div>"
                        +"<div class='sk-cube sk-cube3'></div>"
                        +"<div class='sk-cube sk-cube4'></div>"
                        +"<div class='sk-cube sk-cube5'></div>"
                        +"<div class='sk-cube sk-cube6'></div>"
                        +"<div class='sk-cube sk-cube7'></div>"
                        +"<div class='sk-cube sk-cube8'></div>"
                        +"<div class='sk-cube sk-cube9'></div>"
                        +"</div>"
        });  
    }

    componentDidMount() {
        
        API.post(Urls.fastLinkToken(), null)
        .done(function(res){
            console.log(res);
        	const token = res.finappAuthenticationInfos[0].token;
            const rsession = res.rsession;

            $('#token').val(token);
            $('#rsession').val(rsession);

            $('#fastLink').submit();

        }.bind(this)) 
        .fail(function(e){
            console.log(e);
            window.location.href = Urls.loginPage() + "?next=" +  Urls.linkAccount();
        }.bind(this));
        
    }
    render() {
        return (
            <form id='fastLink' action="https://node.developer.yodlee.com/authenticate/restserver/" method="POST">
                <input type="text" name="app" value="10003600" />
                <input id="rsession" type="text" name="rsession" />
                <input id="token" type="text" name="token" /> 
                <input type="text" name="redirectReq" value="true"/> 
                <input type='text' name='extraParams' placeholer='Extra Params' value={'callback=' + getRootUrl() + "/data/update"}id='extraParams'/>
                <input type="submit" /> 
            </form>
        );
    }
}

export default LinkAccountView;
