import React from 'react';
import { ModuleConst } from '../../const/module.const';
import API from '../../../../js/api';

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
        data: [],
        color: "#F24258",
        dataLabels:{
            enabled : false,
        }
    },
    {
        name: '<p style="color : #434778">Benchmark - S&P 500</p>',
        data: [],
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
    }

    getData(){
        API.get(Urls.broker(this.props.endpoint))
        .done(function(res){
            console.log(res);
            config.series[0].data = res.data.returns;
            config.series[1].data = res.data.benchMark;
            $("#" + ModuleConst.BASIC_RETURN).highcharts(config);

        }.bind(this))
        .fail(function(e){
            console.log(e);
        });
    }
    
    render() {
        return <div style={style} id={ModuleConst.BASIC_RETURN}></div>;
    }
}

export default BasicReturnModule;
