import React from 'react';
import ReactDOM from 'react-dom';
import RegistrationView from '../registration/registrationView.jsx';


ReactDOM.render(<RegistrationView setUpUserID={GLOBAL.setUpUserID} email={GLOBAL.email}/>, document.getElementById("app"));