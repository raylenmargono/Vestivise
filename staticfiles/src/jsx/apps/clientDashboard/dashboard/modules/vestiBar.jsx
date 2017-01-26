import React, {Component} from 'react';
import Highcharts from 'highcharts';

var config = {};

config.title = {
  text: '',
};

config.xAxis = {
    categories: [
    ],
};

config.yAxis = {
    title: {
        text: '',
    },
    gridLineColor: 'transparent',
    plotLines : [{
        color: '#E6E6E6',
        width: 1,
        value: 0
    }]
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

config.tooltip =  {
    formatter: null
}

class VestiBar extends Component{

    constructor(props){
        super(props);
    }

    renderChart(){
        const payload = this.props.payload;
        config.yAxis.title.text = payload.title;
        config.tooltip.formatter = payload.formatter;
        config.xAxis.categories = payload.categories;
        config.series = [];
        for(var i in payload.data){
            var datapoints = payload.data[i];
            const el = {
                name: '<p>' + datapoints.name +'</p>',
                data: datapoints.data,
                color: colors[i],
                dataLabels:{
                    enabled : false,
                },
                useHTML : true
            }
            config.series.push(el);
        }

        Highcharts.chart(this.props.name, config);
    }

    componentDidMount(){
        this.renderChart();
    }

    render(){
        return(
            <div className="vestiBar" id={this.props.name}></div>
        );
    }

}


export default VestiBar;