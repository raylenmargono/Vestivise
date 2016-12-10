import React, {Component} from 'react';
import stripesImg from 'media/stripes.png';

class VestiBlock extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount(){
        function percentage_charts(){
            var chart = $(this),
                chart_section = chart.children(),
                chart_percentage = chart.attr('data-per'),
                chart_title = chart.attr('data-title');
            chart.css('width',chart_percentage + '%').append('<span><h3>' + chart_percentage + '% ' + chart_title + '</h3>');
            if(chart_section.length > 0){
                chart_section.each(function(){
                    var section = $(this),
                        section_percentage = section.attr('data-per'),
                        section_percentage_total = section_percentage/100*chart_percentage,
                        section_title = section.attr('data-title');
                    section.css('width',section_percentage + '%').append('<span><h3>' + section_percentage_total + '% ' + section_title + '</h3>');
                })
            }
        }
        $('.percentage_chart ul').each(percentage_charts);
    }

    getStripped(){
        return {
            "background": "rgba(0,0,0,.1) url(" + stripesImg + ") center/120px repeat"
        }
    }

    render(){
        return(
            <div className="chart percentage_chart">
                <ul data-per="28" data-title="Cash">

                    <li data-per="50" data-title="Cash 1" style={this.getStripped()}/>
                    <li data-per="50" data-title="Cash 2"/>
                </ul>
                    <ul data-per="37" data-title="Bonds"></ul>
                    <ul data-per="26" data-title="Stocks">
                        <li data-per="70" data-title="Stock 1"/>
                        <li data-per="30" data-title="Stock 2"/>
                    </ul>
                <ul data-per="9" data-title="Others"></ul>
            </div>
        );
    }

}


export default VestiBlock;