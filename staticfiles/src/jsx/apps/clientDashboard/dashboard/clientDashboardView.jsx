import React, {Component} from 'react';

class ClientDashboardView extends Component{

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

    render(){
        return(
            <div>
                <div className="section">
                    <div className="row">
                        <div className="chart-container valign-wrapper">
                            <div className="col m2 left-align">
                                <button className="btn-flat nav-button">
                                    <i className="material-icons">navigate_before</i>
                                </button>
                            </div>
                            <div className="col m8 chart percentage_chart">

                                <ul data-per="28" data-title="Cash">

                                    <li data-per="50" data-title="Cash 1"/>
                                    <li data-per="50" data-title="Cash 2"/>
                                </ul>
                                    <ul data-per="37" data-title="Bonds"></ul>
                                    <ul data-per="26" data-title="Stocks">
                                        <li data-per="70" data-title="Stock 1"/>
                                        <li data-per="30" data-title="Stock 2"/>
                                    </ul>
                                <ul data-per="9" data-title="Others"></ul>

                            </div>
                            <div className="col m2 right-align">
                                <button className="btn-flat nav-button">
                                    <i className="material-icons">navigate_next</i>
                                </button>
                            </div>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col m4">
                            <h5>Section 1</h5>
                            <p className="grey-text">SStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStuffStufftuff</p>
                        </div>
                    </div>
                </div>
                <div className="container section">

                </div>
                <div className="container section">

                </div>
                <div className="container section">

                </div>
            </div>
        );
    }

}


export default ClientDashboardView;