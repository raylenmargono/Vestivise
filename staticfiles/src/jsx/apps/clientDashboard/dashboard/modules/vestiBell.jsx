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
    categories: [],
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
    type: 'areaspline'
};

config.series= [{
    name : "test",
    data : []
}];


config.credits = {
    enabled: false
};

class VestiBell extends Component{

    constructor(props){
        super(props);
        this.state = {
            bellX : 5
        }
    }

    createBellCurveData(){
        var payload = this.props.payload;
        var sigma = payload.sigma;
        var mean = payload.mean;
        var right = [];
        var left = [];
        for(var i = 0 ; this.state.bellX > i ; i++){
            var f = 1/(Math.sqrt(2 * Math.PI) * sigma * sigma);
            var e = Math.pow(Math.E, (-Math.pow(((mean+i*2*sigma * sigma/this.state.bellX )-mean), 2))/(2 * sigma));
            var value = f * e;
            right.push(value);
            left.unshift(value);
        }
        var result = left;
        result = result.concat(right.splice(1));
        return result;
    }

    getXAxis(){
        var payload = this.props.payload;
        var sigma = payload.sigma;
        var mean = payload.mean;
        var left = [];
        var result = [mean];
        for(var i = 1 ; i < this.state.bellX ; i++){
            result.push(i * sigma);
            left.unshift(-i * sigma);
        }
        var result = left.concat(result);
        return result;
    }

    shouldComponentUpdate(nextProps){
        return  JSON.stringify(nextProps) !== JSON.stringify(this.props);
    }

    renderChart(){
        config.series[0].data = this.createBellCurveData();
        //config.xAxis.categories = this.getXAxis();
        Highcharts.chart('bell-container', config);
    }

    componentDidMount(){
        this.renderChart();
    }

    componentDidUpdate(){
        this.renderChart();
    }

    render(){
        return(
            <div className="chart" id="bell-container"></div>
        );
    }

}


export default VestiBell;