/**
 * Created by raylenmargono on 12/15/16.
 */
import React, {Component} from 'react';
import Highcharts from 'highcharts';


var config = {};

config.title = {
  text: '',
  style: {
    color : "#000000"
  }
};

config.chart = {
    type: 'area',
    backgroundColor: null,
}

config.xAxis = {
    tickmarkPlacement: 'on',
    title: {
        enabled: false
    },
    labels: {
        enabled: true,
        formatter: null
    },
    startOnTick: false,
    endOnTick: false,
    minPadding: 0,
    maxPadding: 0,
}

config.yAxis = {
    startOnTick: false,
    title: {
        text: ''
    },
    gridLineColor: 'white',
    labels: {
        style: {
            color : '#434778'
        }
    },
    min:0,
    startOnTick: false,
    endOnTick:false
}

config.plotOptions = {
    area: {
        lineColor: '#666666',
        lineWidth: 1,
        marker: {
            enabled: false,
            symbol: 'circle',
            radius: 2,
            states: {
                hover: {
                    enabled: true
                }
            }
        },
        pointStart : 0
    },
    series : {
        fillOpacity: 1
    }
}

config.credits = {
    enabled: false
};

config.series = [];

class VestiAreaLine extends Component{

    constructor(props){
        super(props);
    }

    shouldComponentUpdate(nextProps){
        return JSON.stringify(nextProps) !== JSON.stringify(this.props);
    }

    renderChart(){
        const payload = this.props.payload;
        config.series = payload.data;
        config.xAxis.labels.formatter = function () {
            return payload.categories[this.value];
        };
        Highcharts.chart('area-line-container', config);
    }

    componentDidMount(){
        this.renderChart();
    }

    componentDidUpdate(){
        this.renderChart();
    }

    render(){
        return(<div id="area-line-container"></div>);
    }

}


export default VestiAreaLine;