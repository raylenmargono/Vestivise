import React, {Component} from 'react';
import {GroupActions} from 'jsx/apps/hrDashboard/dashboard/actionModalViews/actionModal.jsx';

class EmployeeTableRow extends Component{

    constructor(props){
        super(props);
    }

    getActiveStatus(){
        if(this.props.employeeData.is_active){
            return "Active";
        }
        return "Pending";
    }

    selectUserForEdit(){
        const id = this.props.employeeData.id;
        const trueIndex = this.props.trueIndex;
        this.props.editAction.modalOption({
            id : id,
            trueIndex : trueIndex,
            action : GroupActions.Detail,
            email : this.props.employeeData.email
        });
    }

    render(){
        return(
            <tr>
                <td>{this.props.index}</td>
                <td>{this.props.employeeData.email}</td>
                <td>{this.getActiveStatus()}</td>
                <td>
                    <button
                        onClick={this.selectUserForEdit.bind(this)}
                        data-target="edit-modal"
                        className="waves-effect waves-light btn-floating"
                    >

                        <i className="material-icons left">edit</i>
                    </button>
                </td>
            </tr>
        );
    }

}


export default EmployeeTableRow;