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
    useHTML : true
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
    }
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
}

config.credits = {
	enabled : false
};

var pie = {
    dataLabels: {
        enabled: true,
        distance: -50,
        style: {
            color: 'white',
            textShadow : false
        }
    },
    startAngle: -90,
    endAngle: 90,
    center: ['50%', '95%'],
    size: "140%"
};

var gauge = {
    dataLabels: {
        enabled: false
    },
    dial: {
        radius: '100%',
        backgroundColor : 'white'
    },
    pivot : {
        radius : 1,
        backgroundColor : "white"
    }
}

config.plotOptions = {
	pie: pie,
	gauge : gauge
};

config.series = [{
    type: 'pie',
    name: 'Risk',
    data: [
	        {
	            name: 'Bad',
	            y : 33,
	            color: "#FFA724"
	        },
	        {
	            name: 'Moderate',
	            y : 33,
	            color: "#FFDB6D"
	        },
	        {
	            name: 'Good',
	            y : 33,
	            color: "#B8D86B"
	        },
    	]
	},
	{
	    type: 'gauge',
	    data: [33],
	    dial: {
	        rearLength: 0,
	        baseWidth : 1
    }
}];

class VestiCategory extends Component{

    constructor(props){
        super(props);
    }

    renderChart(){
        config.series[1].data = [this.props.payload.category];
        const title = '<p class="tooltipped" data-position="top" data-delay="50" >' + this.props.payload.title + '.</p>';
        config.title.text = title;
        for(var i in this.props.payload.colors){
            var color = this.props.payload.colors[i];
            config.series[0].data[i].color = color;
        }
        Highcharts.chart("category-container", config);
    }

    shouldComponentUpdate(nextProps){
        return  JSON.stringify(nextProps) !== JSON.stringify(this.props);
    }

    componentDidUpdate(){
        this.renderChart();
    }

    componentDidMount(){
        this.renderChart();
    }

    render(){
        return(<div className="chart" id="category-container"></div>);
    }

}


export default VestiCategory;