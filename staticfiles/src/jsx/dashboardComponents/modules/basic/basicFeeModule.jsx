import React from 'react';
import { ModuleConst } from '../../const/module.const';
import API from '../../../../js/api';

const style = {
	height: '100%'
};

var gaugeOption = {};

gaugeOption.chart = {
    type: 'solidgauge',
    backgroundColor: "#BBDEFB",
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
        backgroundColor: null,
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
        [0.1, '#55BF3B'], // green
        [0.5, '#DDDF0D'], // yellow
        [0.9, '#DF5353'] // red
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
    data: [],
    dataLabels: {
        format: '<div style="text-align:center; margin-bottom: 15px;"><span style="font-size:25px;color:' +
            ('#333366') + '">{y}%</span><br/>' +'</div>',
        y: 0
    },
    tooltip: {
        valueSuffix: '%'
    }
}];


class BasicFeeModule extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'BasicFeeModule';
    }

    setFee(fee){
        fillOption.series[0].data.push(Number(fee));
    }

    setTitleText(averagePlacement){
        const text = '<p style="margin-top: 0" class="tooltipped" data-position="bottom" data-delay="50" data-tooltip="">Your fees are ' 
                    + averagePlacement 
                    + ' than the majority of investors</p>';
            gaugeOption.title.text = text;
    }

    componentDidMount() {
    	this.getData();
    }

    getData(){
        API.get(Urls.broker(this.props.endpoint))
        .done(function(res){
            this.setTitleText(res.averagePlacement);
            this.setFee(res.fee);
            $("#" + ModuleConst.BASIC_FEE).highcharts(Highcharts.merge(gaugeOption, fillOption));
        }.bind(this))
        .fail(function(e){
            console.log(e);
        });
    }

    render() {
        return <div style={style} id={ModuleConst.BASIC_FEE}></div>;
    }
}

export default BasicFeeModule;
