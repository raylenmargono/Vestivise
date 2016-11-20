import React from 'react';
import { ModuleConst } from '../../const/module.const';
import API from '../../../../js/api';

const style = {
    height : "100%"
};

var config = {};

config.chart = {
    backgroundColor: "#BBDEFB"
};

config.title = {
   text: '', 
   style : {
      color : "#333366"
   }  
};      

config.tooltip = {
   pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
};

config.plotOptions = {
   pie: {
      allowPointSelect: true,
      cursor: 'pointer',
      dataLabels: {
         enabled: true,
         format: '{point.name}: {point.percentage:.3f} %',
         style: {
            textShadow: false
         }
      }
   }
};

config.series= [{
   type: 'pie',
   name: 'Share',
   allowPointSelect: false,
   data: [],
   dataLabels : {
      color : '#333366'
   }
}];

config.credits = {
    enabled: false
};

var colors = ['#2980b9', '#e74c3c', '#2ecc71', "#8e44ad"];

class BasicAssetModule extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'BasicAssetModule';
    }

    createBreakAssetBreakdown(percentages){
        var result = [];
        for(var item in percentages){
            result.push(
                {
                    name : item.replace(/([A-Z])/g, ' $1').trim(),
                    y : percentages[item],
                    color : colors.pop()
                }
            );
        }
    	
        config.series[0].data = result;
    }

    createTitle(totalAssets){
        var stringForm = parseInt(totalAssets).toString();
        stringForm = stringForm.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");

    	config.title.text = 'You have $' + stringForm + ' invested.';
    }

    getData(){
        API.get(Urls.broker(this.props.endpoint))
        .done(function(res){
            this.createTitle(res.data.totalInvested);
            this.createBreakAssetBreakdown(res.data.percentages);
            $("#" + ModuleConst.BASIC_ASSET).highcharts(config);
        }.bind(this))
        .fail(function(e){
            console.log(e);
        });
    }

    componentDidMount() {
        this.getData();
    }

    render() {
        return <div style={style} id={ModuleConst.BASIC_ASSET}></div>;
    }
}

export default BasicAssetModule;
