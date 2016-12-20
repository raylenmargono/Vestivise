import React, {Component} from 'react';
import EmployeeTableRow from './employeeTableRow.jsx';
import EmployeeTablePagination from './employeeTablePagination.jsx';

class EmployeeTable extends Component{

    constructor(props){
        super(props);
    }


    getTableRows(){
        var results = [];
        this.props.employees.forEach(function(employee){
            results.push(<EmployeeTableRow employeeData={employee} key={employee.email} />)
        })
        return results;
    }

    render(){
        return(
            <div className="card">
                <div className="card-stacked">
                    <div id="employee-table" className="card-content">
                        <div className="row">
                            <div className="col m12">
                                <table  className="highlight">
                                    <thead>
                                        <tr>
                                            <th data-field="id">#</th>
                                            <th data-field="email">Email</th>
                                            <th data-field="status">Status</th>
                                            <th data-field="edit"></th>
                                        </tr>
                                    </thead>

                                    <tbody>
                                        {this.getTableRows()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    <div id="pagination-container">
                        <EmployeeTablePagination
                            currentPage={this.props.currentPage}
                            paginationCount={this.props.paginationCount}
                            employeeCount={this.props.employees.length}
                            totalCount={this.props.employeeCount}
                        />
                    </div>
                </div>
            </div>
        );
    }

}


export default EmployeeTable;