import React, {Component} from 'react';
import LoginPage from 'jsx/base/loginPage.jsx';

class ClientLogin extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div>
                <LoginPage method={Urls.login()} dashboardUrl={Urls.home()} />
            </div>
        );
    }

}


export default ClientLogin;