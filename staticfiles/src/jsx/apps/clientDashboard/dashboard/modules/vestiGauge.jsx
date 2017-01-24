import React, {Component} from 'react';
import Highcharts from 'highcharts';
import HighChartsMore from 'highcharts-more';
import HighChartsSolidGauge from 'highcharts-solid-gauge';

HighChartsMore(Highcharts);
HighChartsSolidGauge(Highcharts);


function styleTickLines(id) {
    var paths = $("#" + id + ' .highcharts-axis > path').splice(0);
    var i = 1;
    for(var p in paths){
        if(paths[p].getAttribute("stroke") == "#666"){
            if(i != 2){
                paths[p].setAttribute('opacity', 0);
            }
            i++;
        }
    }
}

var gaugeOption = {};

gaugeOption.chart = {
    type: 'solidgauge',
    backgroundColor: null,
    spacingBottom: 40,
    height: 550
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
    size : "100%",
    center: ['50%', '88%']
};

gaugeOption.tooltip = {
	enabled : false
};

gaugeOption.yAxis = {
    zIndex: 7,
    stops: [
        [0.1, '#ffa724'], // green
        [0.5, '#ffdb6d'], // yellow
        [0.9, '#b8d86b'] // red
    ],
    min: 0,
    max: 0,
    minorTickLength: 0,
    lineWidth: 0,
    tickPixelInterval: 30,
    tickWidth: 5,
    tickPosition: 'inside',
    tickLength: 100,
    tickColor: '#666',
    tickPositions: [],
    labels: {
        style : {
            fontSize : 15,
        },
        format : "{value}%",
        distance: 50,
        formatter : null
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

fillOption.credits = {
	enabled: false
};

fillOption.series = [{
    name: 'Fees',
    data: [1.4],
    dataLabels: {
        format: '<div style="text-align:center; margin-bottom: 30px;"><span style="font-size:40px;color:' +
            ('#333366') + ';font-weight: 100;">{y}%</span><br/>' +'</div>',
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

    renderChart(){
        const payload = this.props.payload;
        gaugeOption.yAxis.tickPositions  = payload.tickPositions;
        gaugeOption.yAxis.max  = payload.max;
        gaugeOption.yAxis.min  = payload.min;
        gaugeOption.yAxis.labels.formatter = payload.formatter;

        fillOption.series[0].name = payload.title;
        fillOption.series[0].data[0] = payload.data;

        gaugeOption.chart.events = {
            load: styleTickLines.bind(this, this.props.name),
            redraw: styleTickLines.bind(this, this.props.name)
        }

        Highcharts.chart(this.props.name, Highcharts.merge(gaugeOption, fillOption));
    }

    componentDidMount(){
        this.renderChart();
    }

    render(){
        return(<div id={this.props.name}></div>);
    }

}


export default VestiGauge;