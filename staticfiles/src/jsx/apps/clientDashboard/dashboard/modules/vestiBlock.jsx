import React, {Component} from 'react';
import stripesImg from 'media/stripes.png';


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

function percentage_charts(){
    var chart = $(this),
        chart_section = chart.children(),
        chart_percentage = (Number(chart.attr('data-per'))).toFixed(1),
        chart_title = chart.attr('data-title');
    //chart.css('width',chart_percentage + '%').append('<span><h3>' + chart_percentage + '% ' + chart_title + '</h3>');
    if(chart_section.length > 0){
        chart_section.each(function(){
            var section = $(this),
                section_percentage = section.attr('data-per'),
                section_percentage_total = (section_percentage/100*chart_percentage).toFixed(1),
                section_title = section.attr('data-title');
            // if(section_percentage > 1){
            //     section.css('width',section_percentage + '%').append('<span><h3>' + section_percentage_total + '% ' + section_title + '</h3>');
            // }
        });
    }
}

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
            result['background'] = "rgba(0,0,0,.1) url(" + stripesImg + ") center/120px repeat";
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

    componentDidMount(){
        $('.percentage_chart ul').each(percentage_charts);
    }

    componentDidUpdate(){
        $('.percentage_chart ul').each(percentage_charts);
    }

    getStripped(){
        return {
            "background": "rgba(0,0,0,.1) url(" + stripesImg + ") center/120px repeat"
        }
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