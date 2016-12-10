import React, {Component} from 'react';

class ChartSlider extends Component{

    constructor(props){
        super(props);
    }

    render(){
        return(
            <ul id="chart-slider">
                <li data-scroll="chart-assets"></li>
                <li data-scroll="chart-returns"></li>
                <li data-scroll="chart-risks"></li>
                <li data-scroll="chart-costs"></li>
            </ul>
        );
    }

}


export default ChartSlider;