import React, {Component} from 'react';
import {ModuleFactory} from './factories/module/moduleFactory.jsx';
import DescriptionFactory from './factories/descriptionFactory.jsx';
import Slider from 'react-slick';

const slickOptions = {
    speed:600,
    infinite:false,
    slidesToShow:1,
    variableWidth:false,
    focusOnSelect:false,
    Autoplay:true,
    autoplaySpeed:1000,
    dots:false,
    arrows:true,
}

class ModuleSection extends Component{

    constructor(props){
        super(props);
    }

    getModules(){
        var modules = this.props.stack.getList();
        var result = [];
        for(var i in modules){
            var module = modules[i];
            result.push(
                <div className="slick-slider" key={module.getName()}>
                    <div className="row">
                        <div className="chart-container valign-wrapper">
                            <div className="col m12">
                                <ModuleFactory
                                    dataAction={this.props.dataAction}
                                    module={module}
                                    dataAPI={this.props.dataAPI}
                                />
                            </div>
                        </div>
                    </div>
                    <DescriptionFactory
                        module={module}
                        appAction={this.props.appAction}
                    />
                </div>
            );
        }
        return result;
    }

    render(){
        var type = this.props.stack.type;
        slickOptions.prevArrow = <button id={"sp-" + type} className="slick-prev"><hr/><hr/></button>;
        slickOptions.nextArrow = <button id={"sn-" + type} className="slick-next"><hr/><hr/></button>;
        return(
            <Slider {...slickOptions}>
                {this.getModules()}
            </Slider>
        );
    }

}


export default ModuleSection;