import React, {Component} from 'react';
import Highcharts from 'highcharts';
import HighChartsMore from 'highcharts-more';
import HighChartsSolidGauge from 'highcharts-solid-gauge';

HighChartsMore(Highcharts);
HighChartsSolidGauge(Highcharts);

var gaugeOption = {};

gaugeOption.chart = {
    type: 'solidgauge',
    backgroundColor: null,
    spacingBottom: 40
};

gaugeOption.title = {
    text : "",
    style : {
        color : "#333366",
    },
    verticalAlign: 'bottom',
    useHTML : true
};

gaugeOption.pane = {
    startAngle: -90,
    endAngle: 90,
    background: {
        backgroundColor: "#DDDDDD",
        innerRadius: '60%',
        outerRadius: '100%',
        shape: 'arc'
    },
    size : "130%",
    center: ['50%', '88%']
};

gaugeOption.tooltip = {
	enabled : false
};

gaugeOption.yAxis = {
    stops: [
        [0.1, '#ffa724'], // green
        [0.5, '#ffdb6d'], // yellow
        [0.9, '#b8d86b'] // red
    ],
    lineWidth: 0,
    minorTickInterval: null,
    tickWidth: 0,
    tickPositions : [0, 2.5],
    labels: {
        y: 16,
        style : {
            color : "#333366"
        },
        format : "{value}%"
    }
};

gaugeOption.plotOptions = {
    solidgauge: {
        dataLabels: {
            y: 5,
            borderWidth: 0,
            useHTML: true
        }
    }
};

var fillOption = {};

fillOption.yAxis = {
	min: 0,
    max: 2.5
};

fillOption.credits = {
	enabled: false
};

fillOption.series = [{
    name: 'Fees',
    data: [1.4],
    dataLabels: {
        format: '<div style="text-align:center; margin-bottom: 15px;"><span style="font-size:25px;color:' +
            ('#333366') + '">{y}%</span><br/>' +'</div>',
        y: 0
    },
    tooltip: {
        valueSuffix: '%'
    }
}];

class VestiGauge extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount(){
        Highcharts.chart("gauge-container", Highcharts.merge(gaugeOption, fillOption));
    }

    render(){
        return(<div id="gauge-container" className="graph"></div>);
    }

}


export default VestiGauge;