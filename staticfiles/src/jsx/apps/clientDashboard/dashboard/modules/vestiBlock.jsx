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
                "#cbdf8c",
                "#9cbdbe",
                "#f79594",
                "#e6ded5",
                "#b8d86b",
                "#dddddd",
                "#2c3e50",
                "#3498db"
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
        var i = 0;
        for(var group in payload){
            var chart_percentage = (Number(payload[group]['total'])).toFixed(1);
            result.push(
                <ul
                    key={group}
                    style={
                        {
                            "width" : chart_percentage + "%",
                            "backgroundColor" : this.state.colors[i++ == this.state.colors.length ? 0 : i]
                        }
                    }
                >
                    <span><h3>{chart_percentage}%  {group} </h3></span>
                    {this.getSubGroups(payload[group]['subgroup'])}
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