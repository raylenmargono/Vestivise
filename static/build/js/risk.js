var gaugeOptions = {

        chart: {
            type: 'solidgauge',
            backgroundColor : "#9C27B0" 
        },

        title: "Your risk profile",

        pane: {
            center: ['50%', '85%'],
            size: '140%',
            startAngle: -90,
            endAngle: 90,
            background: {
                backgroundColor: "#9C27B0",
                innerRadius: '60%',
                outerRadius: '100%',
                shape: 'arc'
            }
        },

        tooltip: {
            enabled: false
        },

        // the value axis
        yAxis: {
            stops: [
                [0.1, '#55BF3B'], // green
                [0.5, '#DDDF0D'], // yellow
                [0.9, '#DF5353'] // red
            ],
            lineWidth: 0,
            minorTickInterval: null,
            tickPixelInterval: 400,
            tickWidth: 0,
            title: {
                y: -70
            },
            labels: {
                y: 16
            },
            min: 0,
            max : 100,
            labels: {
                style : {
                    color : "white"
                }
            }
        },

        plotOptions: {
            solidgauge: {
                dataLabels: {
                    y: 5,
                    borderWidth: 0,
                    useHTML: true
                }
            }
        }
    };

    // The speed gauge
    $('#riskMod').highcharts(Highcharts.merge(gaugeOptions, {
        yAxis: {
            min: 0,
            max: 100,
            labels : {
                enabled : false
            }
        },

        credits: {
            enabled: false
        },

        series: [{
            name: 'Risk',
            data: [80],
            dataLabels: {
                format: '<div style="text-align:center"><span style="font-size:25px;color:' +
                    ((Highcharts.theme && Highcharts.theme.contrastTextColor) || 'white') + '"> Your Risk Profile</span><br/>' +
                       '<span style="font-size:12px;color:silver"></span></div>'
            },
        }]

    }));