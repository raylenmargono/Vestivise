import React, {Component} from 'react';

class SearchBar extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <div className="row">
                <div className="col m10">
                    <input type="text" placeholder="Search employee by name"/>
                </div>
                <div className="col m2">
                    <button className="valign waves-effect waves-light btn-floating" id="search-button">
                        <i className="material-icons search-icon">search</i>
                    </button>
                </div>
            </div>
        );
    }

}


export default SearchBar;