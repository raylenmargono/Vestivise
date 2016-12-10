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
        "One Year",
        "Two Year",
        "Three Year",

    ],
    labels: {
    style: {
        color : '#434778'
    }
  }
};

config.yAxis = {
  title: {
    text: 'Return Amount',
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

config.series= [{
        name: '<p style="color : black">Returns</p>',
        data: [1, 1, 1],
        color: "#F79594",
        dataLabels:{
            enabled : false,
        }
    },
    {
        name: '<p style="color : black">Benchmark</p>',
        data: [2, 2, 2],
        color: "#9CBDBE",
        dataLabels:{
            enabled : false,
        },
        useHTML : true
    }
];

config.credits = {
    enabled: false
};

class VestiBar extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount(){
        Highcharts.chart('bar-container', config);
    }

    render(){
        return(
            <div className="chart" id="bar-container"></div>
        );
    }

}


export default VestiBar;