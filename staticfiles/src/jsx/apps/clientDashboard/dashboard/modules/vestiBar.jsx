import React, {Component} from 'react';
import Highcharts from 'highcharts';

var config = {};

config.title = {
  text: '',
  style: {
    color : "#000000"
  }
};

config.xAxis = {
    categories: [
    ],
    labels: {
    style: {
        color : '#434778'
    }
  }
};

config.yAxis = {
  title: {
    text: '',
    style: {
      color : "#434778"
    }
  },
  gridLineColor: 'transparent',
  labels: {
    style: {
      color : '#434778'
    }
  }
};

config.plotOptions = {
    line: {
      dataLabels: {
          enabled: true
      },
      enableMouseTracking: true
    },
};

config.chart = {
    backgroundColor: null,
    type: 'column'
};

config.series= [];

const colors = ["#CBDF8C", "#F79594", "#9CBDBE"];

config.credits = {
    enabled: false
};

class VestiBar extends Component{

    constructor(props){
        super(props);
    }

    shouldComponentUpdate(nextProps){
        return  JSON.stringify(nextProps) !== JSON.stringify(this.props);
    }

    renderChart(){
        const payload = this.props.payload;
        config.yAxis.title.text = payload.title;
        config.xAxis.categories = payload.categories;
        config.series = [];
        for(var i in payload.data){
            var datapoints = payload.data[i];
            const el = {
                name: '<p style="color : black">' + datapoints.name + '</p>',
                data: datapoints.data,
                color: colors[i],
                dataLabels:{
                    enabled : false,
                },
                useHTML : true
            }
            config.series.push(el);
        }

        Highcharts.chart('bar-container', config);
    }

    componentDidMount(){
        this.renderChart();
    }

    componentDidUpdate(){
        this.renderChart();
    }

    render(){
        return(
            <div className="chart" id="bar-container"></div>
        );
    }

}


export default VestiBar;