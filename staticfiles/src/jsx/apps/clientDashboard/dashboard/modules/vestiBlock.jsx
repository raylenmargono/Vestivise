import React, {Component} from 'react';

/**
 * Accepts prop payload in form of
 * {
 *  key: {
 *      subgroup : [ {
 *          percentage: num
 *          title : string
 *          shouldStripe : boolean
 *      } ],
 *      total : num
 *  }
 * }
 */


class VestiBlockSection extends Component{

    constructor(props){
        super(props);
        this.state = {
            hover: false
        }
    }

    getStyle(){
        var result = {
            'width' : this.props.percentage + "%"
        };
        if(this.props.shouldStripe){
            result['background'] = "rgba(0,0,0,.1) url('/media/stripes.png') center/120px repeat";
        }
        return result;
    }

    handleHoverEnter(hover){
        this.setState({
            hover: hover
        });
    }

    getDescription(){
        if(this.state.hover){
            return (<span><h3>{this.props.percentage}%  {this.props.title}</h3></span>);
        }
    }

    render(){
        return(
                <li
                    onMouseEnter={this.handleHoverEnter.bind(this,true)}
                    onMouseLeave={this.handleHoverEnter.bind(this,false)}
                    data-per={this.props.percentage}
                    data-title={this.props.title}
                    style={this.getStyle()}
                >
                    {this.getDescription()}
                </li>
        );
    }
}

class VestiBlock extends Component{

    constructor(props){
        super(props);
        this.state = {
            colors : [
                "#C2CFAF",
                "#CBDF8C",
                "#E6DED5",
                "#F9F1CE",
                "#F79594",
                "#9FC1BC",
                "#9CBDBE",
                "#C4DFE9",
                '#F7DDBF',
                '#F0D4D4'
            ]
        }
    }

    shouldComponentUpdate(nextProps){
        return  JSON.stringify(nextProps) !== JSON.stringify(this.props);
    }


    getSubGroups(subgroups){
        const result = [];
        for(var i in subgroups){
            var subgroup = subgroups[i];
            result.push(

                <VestiBlockSection
                    percentage={subgroup.percentage}
                    title={subgroup.title}
                    shouldStripe={subgroup.shouldStripe}
                    key={i + subgroup}
                />
            );
        }
        return result;
    }

    getBlocks(){
        const payload = this.props.payload;
        var result = [];
        var keys = Object.keys(payload.groups);
        var shouldAlternate = payload.shouldAlternate;
        for(var i = 0; i < keys.length; i++){
            var group = payload.groups[keys[i]];
            var chart_percentage = (Number(group['total'])).toFixed(1);
            var c = "";
            if(shouldAlternate){
                const altindex1 = 1 +  4 * (Math.ceil(i/4)-1);
                const altindex2 = 2 +  4 * (Math.ceil(i/4)-1);
                const altindex3 = 3 +  4 * (Math.ceil(i/4)-1);
                switch(i){
                    case altindex1:
                        c = "bottom-li-first";
                        break;
                    case altindex2:
                        c = "top-li-second";
                        break;
                    case altindex3:
                        c = "bottom-li-second";
                        break;
                    default:
                        break;
                }
            }
            var color = "color" in group ? group["color"] : this.state.colors[i];
            result.push(
                <ul
                    key={i}
                    style={
                        {
                            "width" : chart_percentage + "%",
                            "backgroundColor" : color
                        }
                    }
                    className={c}
                >
                    <span>
                        <h3>{chart_percentage}%  {keys[i]} </h3>
                    </span>
                    {this.getSubGroups(group['subgroup'])}
                </ul>
            );
        }
        return result;
    }

    render(){
        return(
            <div className="chart percentage_chart">
                {this.getBlocks()}
            </div>
        );
    }

}


export default VestiBlock;