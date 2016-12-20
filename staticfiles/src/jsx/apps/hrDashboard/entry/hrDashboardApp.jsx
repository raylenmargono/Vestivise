import React from 'react';
import ReactDOM from 'react-dom';
import HRDashboard from '../dashboard/hrDashboardView.jsx';
import AltContainer from 'alt-container';
import HRAppStore from 'js/flux/hrDashboard/stores/hrDashboardStore';
import {EmployeeSearchAction, EmployeeEditAction} from 'js/flux/hrDashboard/actions/actions';

const app = (
    <AltContainer
        actions = {
            {
                EmployeeEditAction : EmployeeEditAction,
                EmployeeSearchAction : EmployeeSearchAction,
            }
        }
        stores = {
            {
                AppState : HRAppStore
            }
        }
    >
        <HRDashboard />
    </AltContainer>
);

ReactDOM.render(app, document.getElementById("app"));