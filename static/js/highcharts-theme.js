Highcharts.theme = {
    chart: {
        style: {
            fontFamily: "'Play', sans-serif"
        }
    },
    title: {
        text: null
    },
    xAxis: {
        gridLineColor: '#eee',
        labels: {
            style: {
                color: '#777',
                fontSize: '1em'
            }
        },
        lineColor: '#eee',
        tickColor: '#eee',
        tickWidth: 1
    },
    yAxis: {
        gridLineColor: '#eee',
        labels: {
            style: {
                color: '#777',
                fontSize: '1em'
            }
        },
        lineColor: '#eee',
        tickColor: '#eee',
        tickWidth: 1
    },
    tooltip: {
        backgroundColor: '#fff',
        borderColor: '#eee',
        style: {
            color: '#333'
        }
    },
    legend: {
        itemStyle: {
            fontWeight: 'normal'
        }
    },
    credits: {
        enabled: false
    }
};
Highcharts.setOptions(Highcharts.theme);

Highcharts.setOptions({
    global: {
        useUTC: false
    },
    lang: {
        thousandsSep: ''
    }
});
