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
                <td><a className="waves-effect waves-light btn-floating"><i className="material-icons left">edit</i></a></td>
            </tr>
        );
    }

}


export default EmployeeTableRow;