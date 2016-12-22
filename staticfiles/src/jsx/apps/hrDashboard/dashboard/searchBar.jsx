import React, {Component} from 'react';

class SearchBar extends Component{

    constructor(props){
        super(props);
    }

    search(e){
        e.preventDefault();
        var value = this.refs.queryTextField.value;
        this.props.searchAction.search(value);
    }

    render(){
        return(
            <form onSubmit={this.search.bind(this)}>
                <div className="row">
                    <div className="col m10">
                        <input ref='queryTextField' type="text" placeholder="Search employee by name"/>
                    </div>
                    <div className="col m2">
                        <button
                            type="submit"
                            className="valign waves-effect waves-light btn-floating" id="search-button">
                            <i className="material-icons search-icon">search</i>
                        </button>
                    </div>
                </div>
            </form>
        );
    }

}


export default SearchBar;