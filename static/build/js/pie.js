
function hideLabel(){
   var chart = $('#assetBreakMod').highcharts();
   var opt = chart.series[0].options;
   opt.dataLabels.enabled = !opt.dataLabels.enabled;
   opt.animation = false;
   chart.series[0].update(opt);
}

var chart = {
    backgroundColor: "#FF9800"
};
var title = {
   text: 'You have $90,000 invested.', 
   style : {
      color : "white"
   }  
};      
var tooltip = {
   pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
};
var plotOptions = {
   pie: {
      allowPointSelect: true,
      cursor: 'pointer',
      dataLabels: {
         enabled: true,
         format: '<b>{point.name}%</b>: {point.percentage:.1f} %',
         style: {
            textShadow: false 
         }
      }
   }
};
var series= [{
   type: 'pie',
   name: 'Share',
   data: [
      {
         name : "Bonds",
         y : 35,
         color : '#2980b9'
      },
      {
         name : "Stocks",
         y : 26.8,
         color : '#e74c3c'
      },
      {
         name: 'Commodities',
         y: 28.8,
         selected: true,
         color : '#2ecc71'
      },
      {
         name : 'Real Estate',
         y: 10,
         color : "#8e44ad"
      }
   ],
   dataLabels : {
      color : 'white'
   }
}]; 

var credits = {
      enabled: false
}
   
var json = {};   
json.chart = chart; 
json.title = title;     
json.tooltip = tooltip;  
json.series = series;
json.plotOptions = plotOptions;
json.credits = credits;
$('#assetBreakMod').highcharts(json);  

var assetOpt = json;
