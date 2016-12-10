import React from 'react';
import ReactDOM from 'react-dom';
import HRDashboard from '../dashboard/dashboardView';
import AltContainer from 'alt-container';
import EmployeeStore from 'js/flux/hrDashboard/stores/employeeStore';
import HRAppStore from 'js/flux/hrDashboard/stores/hrDashboardStore';
import {employeeSearchAction, employeeEditAction, hrAppAction} from 'js/flux/hrDashboard/actions/actions';

const app = (
    <AltContainer
        actions = {
            {
                EmployeeEditAction : employeeEditAction,
                EmployeeSearchAction : employeeSearchAction,
                HRAppAction : hrAppAction
            }
        }
        stores = {
            {
                EmployeeState : EmployeeStore,
                AppState : HRAppStore
            }
        }
    >
        <HRDashboard />
    </AltContainer>
);

ReactDOM.render(app, document.getElementById("app"));