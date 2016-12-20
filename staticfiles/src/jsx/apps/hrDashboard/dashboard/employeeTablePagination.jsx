import React, {Component} from 'react';

class EmployeeTablePagination extends Component{

    constructor(props){
        super(props);
    }

    getPaginationList() {
        const max = this.props.paginationCount;
        const current = this.props.currentPage;
        var size = 4;
        var temp = [current];

        for(var i = 0 ; i / 2 < size ; i++){
            if(current + i + 1 <= max){
                temp.append(current + i + 1);
            }
            if(current - i - 1 > 0){
                temp.unshift(current - i - 1);
            }
        }

        while(temp.length < 5 && temp.length < max + 1){
            if(temp[0] > 1){
                temp.unshift(temp[0] - 1);
            }
            else{
                temp.push(temp[temp.length - 1] + 1);
            }
        }

        var result = [];

        temp.forEach(function(i){
            var c = i == current ? "active" :  "waves-effect";
            result.push(
                <li
                    className={c}
                    key={i}
                    onClick={this.changePage.bind(this, i)}
                >
                    <a href="#!">
                        {i}
                    </a>
                </li>);
        })

        return result;
    }

    getEmployeeCount(){
        var result = " of ";

        var count = this.props.employeeCount;
        var totalCount = this.props.totalCount;
        var page = this.props.currentPage;

        var currentEmployeeCount = count * ( 100 * (page - 1)) + count

        result += currentEmployeeCount + result + totalCount;

        return result;
    }

    changePage(index){
        console.log(index);
    }

    getNavigationClass(type){
        const max = this.props.paginationCount;
        const current = this.props.currentPage;
        if(type == "back" && current == 1){
            return "disabled";
        }
        if(type == "front" && current == max){
            return "disabled";
        }
        return "waves-effect";
    }

    render(){
        return(
            <div className="row">
                <div className="col m6">
                    <ul className="pagination">
                        <li className={this.getNavigationClass("back")}>
                            <a onClick={this.changePage.bind(this, this.props.currentPage - 1)}>
                                <i className="material-icons">
                                    chevron_left
                                </i>
                            </a>
                        </li>
                        {this.getPaginationList()}
                        <li className={this.getNavigationClass("front")}>
                            <a onClick={this.changePage.bind(this, this.props.currentPage + 1)}>
                                <i className="material-icons">
                                    chevron_right
                                </i>
                            </a>
                        </li>
                    </ul>
                    <p>Showing {this.getEmployeeCount()} employees</p>
                </div>
            </div>
        );
    }

}


export default EmployeeTablePagination;