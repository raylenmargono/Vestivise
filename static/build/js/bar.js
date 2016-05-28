var title = {
    	text: 'Your Lost $5,000 this year so far.',
    	style: {
    		color : "white"
    	}
   	};
  
	var xAxis = {
  	categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    	'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
   	labels: {
		style: {
			color : 'white'
		}	
	}
	};

var yAxis = {
	title: {
		text: 'Return Amount',
		style: {
			color : "white"
		}
	},
	gridLineColor: 'transparent',
	labels: {
		style: {
			color : 'white'
		}	
	}
};

var plotOptions = {
  	line: {
    	dataLabels: {
        	enabled: true
    	},   
     	enableMouseTracking: true
  	},
};

var chart = {
  	backgroundColor: "#4CAF50"
};

var dataSource1 = [11.0, 6.9, 9.5, 14.5, 18.4, 21.5, 25.2, 26.5, 23.3, 21.5, 25.2, 26.5];
var dataSource2 = [3, 12, 5, 26, 17, 3, 12, 5, 26, 17, 3, 12];

var series= [{
        name: 'My Returns',
        data: dataSource2,
        color: "white",
        dataLabels:{
            enabled : false,
            color : 'white'
        }
    },
    {
        name: 'Benchmark - S&P 500',
        data: dataSource1,
        color: "#F24258",
        dataLabels:{
            enabled : false,
            color : 'white'
        }
    }
];
   
var json = {};

json.title = title;
json.chart = chart;
json.xAxis = xAxis;
json.yAxis = yAxis;  
json.series = series;
json.plotOptions = plotOptions;
$('#returnPerYearMod').highcharts(json);