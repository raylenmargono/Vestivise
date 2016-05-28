var title = {
    	text: 'Your earned $5000 this year so far',
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
		text: '$',
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

var series= [{
     name: 'Me',
     data: [11.0, 6.9, 9.5, 14.5, 18.4, 21.5, 25.2, 26.5, 23.3, 21.5, 25.2, 26.5, 23.3],
     color: "white",
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