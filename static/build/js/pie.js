var chart = {
    backgroundColor: "#FF9800",
};
var title = {
   text: 'You have $15,000 invested', 
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
   name: 'Browser share',
   data: [
      ['Bonds',   45.0],
      ['Stocks',       26.8],
      {
         name: 'Commodities',
         y: 28.8,
         sliced: true,
         selected: true
      },
   ],
   dataLabels : {
      color : 'white'
   }
}]; 
  
   
var json = {};   
json.chart = chart; 
json.title = title;     
json.tooltip = tooltip;  
json.series = series;
json.plotOptions = plotOptions;
$('#assetBreakMod').highcharts(json);  