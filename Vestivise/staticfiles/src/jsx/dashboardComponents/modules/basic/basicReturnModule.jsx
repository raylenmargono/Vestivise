import React from 'react';
import { ModuleConst } from '../../const/module.const';

const style = {
    height : "100%"
};

var config = {};

config.title = {
  text: '',
  style: {
    color : "#434778"
  }
};
  
config.xAxis = {
    categories: [
        "One Month Return",
        "Three Month Return",
        "One Year Return",
        "Three Year Return"
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
        name: '<p style="color : #434778">My Returns</p>',
        data: [1, 1, 1, 1],
        color: "#F24258",
        dataLabels:{
            enabled : false,
        }
    },
    {
        name: '<p style="color : #434778">Benchmark - S&P 500</p>',
        data: [0.48,4.06,4.70,8.94],
        color: "rgb(66,153,210)",
        dataLabels:{
            enabled : false,
        },
        useHTML : true
    }
];

config.credits = {
    enabled: false
};
   
class BasicReturnModule extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'BasicReturnModule';
    }

    componentDidMount() {
    	this.getData();
        console.log
    	$("#" + ModuleConst.BASIC_RETURN).highcharts(config);
    }

    getData(){
        if(this.props.data){
            config.series[0].data = this.props.data["returns"];
            config.series[1].data = this.props.data["benchMark"];
        }
    }

    // getTitle(){
    // 	var title = "";
    // 	if(this.props.data){
    // 		const benchmarked = this.props.data.benchmarked;
    // 		const n = Number(benchmarked);
    // 		var lostOrGain = n < 0 ? "lost" : "gained";
    // 		title = "You have " + lostOrGain + " $" + Math.abs(n) + " this year so far.";

    // 	}
    // 	config.title.text = title;
    // }

    // getTimeScale(){
    // 	if(this.props.data){
    // 		config.xAxis.categories = this.props.data.timeScale.map(function (data) {
    // 									return data.month + " " + data.year;
    // 								});

    // 	}
    // }
    
    // getPerformance(){
    // 	if(this.props.data){
    // 		config.series[0].data = this.props.data.fundPerformance.map(function (data) {
    // 									return Number(data.returns);
    // 								});
    // 		config.series[1].data = this.props.data.benchMarkPerformance.map(function (data) {
    // 									return Number(data.returns);
    // 								});

    // 	}
    // }
    
    render() {
        return <div style={style} id={ModuleConst.BASIC_RETURN}></div>;
    }
}

export default BasicReturnModule;
