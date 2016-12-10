import React, {Component} from 'react';
import VestiBlock from './modules/vestiBlock.jsx';
import VestiBar from './modules/vestiBar.jsx';
import VestiCategory from './modules/vestiCategory.jsx';
import VestiGauge from './modules/vestiGauge.jsx';
import Highcharts from 'highcharts';

Highcharts.setOptions({
    chart: {
        style: {
            fontFamily: 'Graphik,Helvetica,Arial,sans-serif'
        }
    }
});

const ModuleType = {
    BLOCKS : 'BLOCKS',
    BAR : 'BAR',
    GAUGE : 'GAUGE',
    CONTENT : 'CONTENT',
    CATEGORY : 'CATEGORY'
}

class ModuleFactory extends Component{

    constructor(props){
        super(props);
    }

    getModule(){
        switch(this.props.type){
            case ModuleType.BLOCKS:
                return <VestiBlock />
            case ModuleType.CATEGORY:
                return <VestiCategory />;
            case ModuleType.BAR:
                return <VestiBar />
            case ModuleType.CONTENT:
                break;
            case ModuleType.GAUGE:
                return <VestiGauge />;
            default:
                return null;
        }
    }

    render(){
        return(
            <div>
                {this.getModule()}
            </div>
        );
    }

}

export {ModuleType, ModuleFactory}
