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
            c += " btn";
            result.push(<li key={i} className={c}><button href="#!">{i}</button></li>);
        })

        return result;
    }


    render(){
        return(
            <ul className="pagination">
                <li className="disabled"><button className="btn"><i className="material-icons">chevron_left</i></button></li>
                {this.getPaginationList()}
                <li className="waves-effect"><button className="btn"><i className="material-icons">chevron_right</i></button></li>
            </ul>
        );
    }

}


export default EmployeeTablePagination;