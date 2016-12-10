import React, {Component} from 'react';

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

    render(){
        return(
            <tr>
                <td>{this.props.employeeData.id}</td>
                <td>{this.props.employeeData.email}</td>
                <td>{this.getActiveStatus()}</td>
            </tr>
        );
    }

}


export default EmployeeTableRow;