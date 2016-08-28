import React from 'react';

const style={
	'backgroundColor' : "white"
}

class HoldingEditorPane extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'HoldingEditorPane';

    }

    getClass(key){
    	if(this.props.data[key]){
    		return 'validate active';
    	}
    	return 'validate';
    }

    getHeader(){
    	return this.props.data.description;
    }

    commitChanges(){
    	const payload = {
    		"cusipNumber" : this.refs.cusipNumber.value,
    		"symbol" : this.refs.symbol.value,
    		"ric" : this.refs.ric.value,
    		"completed" : true
    	}

    	this.props.editHolding(payload, this.props.data.id, this.props.index);
    }

    render() {
        return (
        	<div className='card'>
		      <div className="card-content">
		      	<p className="card-title">{this.getHeader()}</p>
				<div style={style} className="row">
					<div className="input-field col s12">
						<input ref='cusipNumber' id='cusipNumber' defaultValue={this.props.data.cusipNumber} type="text"/>
						<label className={this.getClass("cusipNumber")} htmlFor="cusipNumber">cusipNumber</label>
					</div>
				</div>
				<div style={style} className="row">
					<div className="input-field col s12">
						<input ref='symbol' id='symbol' defaultValue={this.props.data.symbol} type="text"/>
						<label className={this.getClass("symbol")} htmlFor="symbol">symbol</label>
					</div>
				</div>
				<div style={style} className="row">
					<div className="input-field col s12">
						<input ref='ric' id='ric' defaultValue={this.props.data.ric} type="text"/>
						<label className={this.getClass("ric")} htmlFor="ric">ric</label>
					</div>
				</div>

				<div className='row'>
					<div className='col s12'>
						<button onClick={this.commitChanges.bind(this)} className="waves-effect waves-light btn">Commit Changes</button>
					</div>
				</div>

		      </div>
		    </div>
        );
    }
}

export default HoldingEditorPane;
