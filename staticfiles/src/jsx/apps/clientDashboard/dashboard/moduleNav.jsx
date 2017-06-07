import React, {Component} from 'react';

const CurrentModule = {
    ASSET : 0,
    RETURN: 1,
    RISK : 2,
    FEE : 3
};

class ModuleNav extends Component{

    constructor(props){
        super(props);
        this.state = {
            currentModule : CurrentModule.ASSET
        }
    }

    componentDidMount(){
        window.addEventListener('scroll', this.handleScroll.bind(this));
    }

    handleScroll(){
        var scroll_top = $(window).scrollTop();
        var currentModule = "";
        if(scroll_top>=$('#chart-assets').position().top){
            currentModule = CurrentModule.ASSET;
        }
        if(scroll_top>=$('#chart-returns').position().top){
            currentModule = CurrentModule.RETURN;
        }
        if(scroll_top>=$('#chart-risks').position().top){
            currentModule = CurrentModule.RISK;
        }
        if(scroll_top>=$('#chart-costs').position().top){
            currentModule = CurrentModule.FEE;
        }
        this.setState({
            currentModule : currentModule
        });
    }

    scrollTo(div){
        $("html,body").animate({
  		    scrollTop:$(div).offset().top
	    },600);

    }

    getNavBody(){
        const temp = [
            <a key={CurrentModule.ASSET} onClick={this.scrollTo.bind(this, '#chart-assets')}>Assets</a>,
            <a key={CurrentModule.RETURN} onClick={this.scrollTo.bind(this,'#chart-returns')}>Returns</a>,
            <a key={CurrentModule.RISK}  onClick={this.scrollTo.bind(this, '#chart-risks')}>Risks</a>,
            <a key={CurrentModule.FEE} onClick={this.scrollTo.bind(this, '#chart-costs')}>Costs</a>
        ];
        var current = temp.splice(this.state.currentModule, 1);
        return(
            <div>
                <div id="moduleNav-container">
                    {temp}
                </div>
                <div id="main-mod">
                    {current[0]}
                </div>
            </div>
        );
    }

    render(){
        return(
            <div id="moduleNav">
                {this.getNavBody()}
            </div>
        );
    }

}


export default ModuleNav;