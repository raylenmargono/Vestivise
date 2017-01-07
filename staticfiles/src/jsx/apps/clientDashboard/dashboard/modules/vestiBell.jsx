import React, {Component} from 'react';
import Highcharts from 'highcharts';

var config = {};

config.title = {
    text: '',
    style: {
        color : "#000000"
    }
};

config.tooltip = {
    pointFormat: "{point.y:.2f}"
}


config.xAxis = {
    title: {
        text: '',
        style: {
            color : "#434778"
        }
    },
    categories: [],
    labels: {
        style: {
            color : '#434778'
        },
        formatter: function() {
            return parseFloat((Math.round(this.value * 100) / 100).toFixed(2));
        },
    },
    plotLines: [{
        color: '#9DBEBF', // Red
        width: 2,
        value: 0,
        label: {
            rotation: 0,
            y: 15,
            text: 'You'
        },
    }]
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
            enabled: false
        },
        enableMouseTracking: true,
        marker: {
            enabled : false
        }
    },
    areaspline : {
        marker: {
            enabled : false
        }
    }
};


config.chart = {
    backgroundColor: null,
    type: 'areaspline'
};

config.series= [{
    name : "",
    data : [],
    color : "#F43E54"
}];


config.credits = {
    enabled: false
};

class VestiBell extends Component{

    constructor(props){
        super(props);
        this.state = {
            bellX : 30
        }
    }

    createBellCurveData(){
        var payload = this.props.payload;
        var sigma = payload.sigma;
        var mean = payload.mean;
        var right = [];
        var left = [];
        for(var i = 0 ; this.state.bellX > i ; i++){
            var f = 1/(Math.sqrt(2 * Math.PI) * sigma);
            var e = Math.pow(Math.E, (-Math.pow(((mean + i*sigma*3/this.state.bellX )-mean), 2))/(2 * sigma * sigma));
            var value = f * e;
            right.push(value);
            left.unshift(value);
        }
        var result = left;
        result = result.concat(right.splice(1));
        return result;
    }

    sortedIndex(array, value) {
        var low = 0,
            high = array.length;

        while (low < high) {
            var mid = (low + high) >>> 1;
            if (array[mid] < value) low = mid + 1;
            else high = mid;
        }
        return low;
    }

    getXAxis(){

        var payload = this.props.payload;
        var sigma = payload.sigma;
        var mean = payload.mean;
        var left = [];
        var result = [mean];
        for(var i = 1 ; i < this.state.bellX ; i++){
            result.push(mean + i*3*sigma/this.state.bellX);
            left.unshift(mean - i*3*sigma/this.state.bellX);
        }
        var result = left.concat(result);
        var insert_index  = this.sortedIndex(result, this.props.payload.user);

        result.splice(insert_index, 0, this.props.payload.user);
        return result;
    }

    renderChart(){
        config.series[0].data = this.createBellCurveData();
        config.series[0].name = this.props.payload.title;
        config.xAxis.categories = this.getXAxis();
        var insert_index  = this.sortedIndex(config.xAxis.categories, this.props.payload.user);
        config.xAxis.plotLines[0].value = insert_index;
        config.xAxis.title.text = this.props.payload.xTitle;
        config.yAxis.title.text = this.props.payload.yTitle;
        Highcharts.chart(this.props.name, config);
    }

    componentDidMount(){
        this.renderChart();
    }

    render(){
        return(
            <div id={this.props.name}></div>
        );
    }

}


export default VestiBell;