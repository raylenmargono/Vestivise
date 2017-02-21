import 'highcharts-more';
import React, {Component} from 'react';
import Highcharts from 'highcharts';
import HighChartsMore from 'highcharts-more';
HighChartsMore(Highcharts);

var config = {};

config.chart = {
	renderTo: "category-container",
    plotBackgroundColor: null,
    plotBackgroundImage: null,
    plotBorderWidth: 0,
    plotShadow: false,
    backgroundColor: null,
    spacingBottom: 40
};

config.title = {
    align: 'center',
    style: {
        color : '#333366'
    },
    verticalAlign: 'bottom',
    useHTML : true,
    text : ""
};

config.pane = {
	center: ['50%', '88%'],
    startAngle: -90,
    endAngle: 90,
    background: {
        borderWidth: 0,
        backgroundColor: 'none',
        innerRadius: '60%',
        outerRadius: '100%',
        shape: 'arc'
    },
};

config.yAxis = [{
    lineWidth: 0,
    min: 0,
    max: 90,
    minorTickLength: 0,
    tickLength: 0,
    tickWidth: 0,
    labels: {
        enabled: false
    },
    title: {
        text: '', //'<div class="gaugeFooter">46% Rate</div>',
        useHTML: true,
        y: 80
    },
    pane: 0,
}];


config.tooltip = {
    enabled : false,
};

config.credits = {
	enabled : false
};

var pie = {
    dataLabels: {
        enabled: true,
        distance: -50,
        style: {
            color: 'white',
            textShadow : false,
            fontWeight : 100,
            fontSize : 15
        }
    },
    startAngle: -90,
    endAngle: 90,
    center: ['50%', '95%'],
    size: "150%"
};

var gauge = {
    dataLabels: {
        enabled: false
    },
    dial: {
        radius: '100%',
        backgroundColor : '',
    },
    pivot : {
        radius : 0,
        backgroundColor : "white",
    }
};

config.plotOptions = {
	pie: pie,
	gauge : gauge
};

config.series = [{
    type: 'pie',
    name: 'Risk',
    data: []
	},
	{
	    type: 'gauge',
	    data: [33],
	    dial: {
	        rearLength: 0,
	        baseWidth : 5
        }
    }
];


class VestiCategory extends Component{

    constructor(props){
        super(props);
    }

    renderChart(){
        var data = [
            {
                name: 'Bad',
                y : 33,
            },
            {
                name: 'Moderate',
                y : 33,
            },
            {
                name: 'Good',
                y : 33,
            },
        ];
        config.series[1].data = [this.props.payload.category];
        for(var i in this.props.payload.colors){
            var color = this.props.payload.colors[i];
            data[i].color = color;
        }
        config.series[0].data = data;
        config.plotOptions.gauge.dial.backgroundColor = this.props.payload.dialColor;
        config.plotOptions.gauge.pivot.backgroundColor = this.props.payload.dialColor;
        Highcharts.chart(this.props.name, config);
    }

    componentDidMount(){
        this.renderChart();
    }

    render(){
        return(<div id={this.props.name}></div>);
    }

}


export default VestiCategory;