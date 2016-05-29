var chart = {
    backgroundColor: "#FF9800",
};
var title = {
   text: 'Equity Sectors', 
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

var data1 = [
               ['Utilities',   9.2],
               ['Consumer Services',       10.8],
               ['Health Care',       30],
               ['Industrials',       30],
               {
                  name: 'Technology',
                  y: 20,
               },
]

var data2 = [
      ['High Yield',  60],
      {
         name: 'US Treasury',
         y: 40,
      },
]

var dataSeries= [{
   type: 'pie',
   name: 'Sector',
   data: data1,
   dataLabels : {
      color : 'white',
      enabled : true
   }
}]; 

var credits = {
      enabled: false
}
   
var json = {};   
json.chart = chart; 
json.title = title;     
json.tooltip = tooltip;  
json.series = dataSeries;
json.plotOptions = plotOptions;
json.credits = credits;

var sectorOpt = json;