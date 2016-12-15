import React, {Component} from 'react';

class ChartSlider extends Component{

    constructor(props){
        super(props);
    }

    componentDidMount(){

        function scroll_to(div){
            $("html,body").animate({
                scrollTop:$(div).offset().top
            },600)

        }

        function chart_slider_init(){
            var chart_slider = $('#chart-slider'),
                chart_slider_li = chart_slider.find('li');

            function chart_slider_active(){
                var scroll_top = $(window).scrollTop();
                $('.section').each(function(){
                    var section = $(this),
                        section_id = section.attr('id'),
                        section_top = section.offset().top;
                    if(scroll_top > section_top - 1){
                        chart_slider.find('[data-scroll="' + section_id + '"]').addClass('active').siblings().removeClass('active')
                    }
                })
            }
            chart_slider_active();
            $(window).scroll(chart_slider_active);

            chart_slider_li.click(function(){
                var chart_scroll = $(this).attr('data-scroll');
                scroll_to('#' + chart_scroll);
            });

        }
        chart_slider_init();
    }

    render(){
        return(
            <ul id="chart-slider">
                <li className="active" data-scroll="chart-assets"></li>
                <li data-scroll="chart-returns"></li>
                <li data-scroll="chart-risks"></li>
                <li data-scroll="chart-costs"></li>
            </ul>
        );
    }

}


export default ChartSlider;