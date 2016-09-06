import React from 'react';
import HoldingEditorPane from './holdingEditorPane.jsx';
import API from '../../js/api.js';

class HoldingEditorView extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'HoldingEditorView';
        this.state = {
            holdings : []
        }
    }

    componentDidMount() {
     	$('.collapsible').collapsible({
      		accordion : true // A setting that changes the collapsible behavior to expandable instead of the default accordion style
        });
        this.getHoldings();
    }

    getHoldings(){
        const url = Urls.holdings() + "?completed=false";
        API.get(url)
        .done(function(res){
            console.log(res);
            this.setState({
                holdings : res
            });
        }.bind(this))
        .fail(function(e){
            console.log(e);
        });

    }

    editHolding(payload, id, index){
        const options = {
            "type" : "PATCH"
        }
        API.put(Urls.holdingDetail(id), payload, options)
        .done(function(res){
            if (index > -1) {
                this.state.holdings.splice(index, 1);
                this.setState({
                    holdings : this.state.holdings
                });
            }
        }.bind(this))
        .fail(function(e){
            conosle.log(e);
        });
    }

    getHoldingPanes(){
        var result = [];
        for (var i = 0 ; this.state.holdings.length  >  i; i++) {
            const holding = this.state.holdings[i];
            result.push(
                <HoldingEditorPane 
                    key={i} 
                    data={holding}
                    index={i}
                    editHolding={this.editHolding.bind(this)}
                />
            );
        }

        if(this.state.holdings.length == 0){
            return <h1>No New Holdings</h1>
        }

        return result;
    }

    render() {
        return (
        	<div className='container'>
        		<div className='row'>
        			<div className='col m12'>
                        {this.getHoldingPanes()}
        			</div>
        		</div>
        	</div>	
        );
    }
}

export default HoldingEditorView;
