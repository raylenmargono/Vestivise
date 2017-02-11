import React, {Component} from 'react';

class VestiTable extends Component{

    constructor(props){
        super(props);
    }

    getHeaders(){
        const headers = this.props.payload.headers;
        var result = [];
        for(var i in headers){
            var header = headers[i];
            result.push(
                <th key={i}>
                    {header}
                </th>
            );
        }
        return result;
    }

    getRows(){
        const rows = this.props.payload.rows;
        var result = [];
        for(var i in rows){
            var row = rows[i];
            var rowData = [];
            for(var j in row){
                rowData.push(<td key={i * 10 + j}>{row[j]}</td>);
            }
            result.push(
                <tr key={i}>
                    {rowData}
                </tr>
            );
        }
        return result;
    }

    render(){
        return(
            <div className="vestiTable" id={this.props.name}>
                <table className="highlight">
                    <thead>
                        <tr>
                            {this.getHeaders()}
                        </tr>
                    </thead>
                    <tbody>
                        {this.getRows()}
                    </tbody>
                </table>
            </div>
        );
    }

}


export default VestiTable;