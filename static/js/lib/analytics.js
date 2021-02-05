
define(['vendor/Chart.bundle.min', 'ajax_api'],
function(Chart, ajax){
    'use strict';
    var dashboardIntervalHandle;
    var order_chart;
    var product_chart;
    var visitors_charts;
    var visitor_charts;
    var unique_visitor_charts;
    var facebook_visitor_charts;
    var suspicious_visitor_charts;
    var order_price_chart;
    var new_user_chart;
    var analytics_label = 'Orders';
    var analytics_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var chart_type = 'bar';
    var line_type = 'line';

    var UPDATE_RATE = 60000 * 5; // 5min 
    var default_scales = {
        xAxes: [
            {
                type: 'time',
                time : {
                    unit: "month",
                    parser : "MM",
                    displayFormats: {
                        month : "MM"
                    }
                },
                distribution: 'series',
                scaleLabel: {
                    display : true,
                    labelString : "Months"
                }
            }
        ]/* ,
        yAxes: [
            {
                scaleLabel: {
                    display : true,
                    labelString : "Count"
                }
            }
        ]
        */
    }
    var orders_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: '',
                data: [],
                backgroundColor: '#0A0A0A'
            }],
        },
        options:{
            scales : default_scales
        }
    };
    var orders_price_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: '',
                data: [],
                backgroundColor: '#0A0A0A'
            }],
        },
        options:{
            scales : {
                xAxes: [
                    {
                        scaleLabel: {
                            display : true,
                            labelString : "Months"
                        }
                    }
                ],
                yAxes: [
                    {
                        scaleLabel: {
                            display : true,
                            labelString : "Price in XAF"
                        }
                    }
                ]
            }
        }
    };

    var products_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: '',
                data: [],
                backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var visitors_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Visitors',
                data: []
                //backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var visitor_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Visitors',
                data: []
                //backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var unique_visitor_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Unique Visitors',
                data: []
                //backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var facebook_visitor_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Facebook Visitors',
                data: []
                //backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };
    var suspicious_visitor_conf = {
        type : line_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Suspicious Visitors',
                data: []
                //backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };
    var new_users_conf = {
        type : chart_type,
        data : {
            labels : [],
            datasets : [{
                label: '',
                data: []
            }],
        },
        options:{
            scales : default_scales
        }
    };
    var report;

    function createDataList(data, months){
        var dataList = [];
        if(data.length != months.length){
            console.warn("inconsistent length");
            return  dataList;
        }else{
            for (var i = 0; i < data.length; i++){
                console.log("x : %s - y : %s", months[i], data[i]);
                dataList.push({x:months[i], y:data[i]})
            }
        }
        return dataList;
    }

    function updateChart(){
        var options = {
            url:'/api/analytics/',
            type:'GET',
            data:{},
            dataType: 'json'
        }
        var promise = ajax(options).then(function(response){
            dispatchChartUpdate(response)
        }, function(error){
            console.log("Orders fetch failed");
            console.log(error);
        });
    }
    function dispatchChartUpdate(response){
        var label = response.label;
        var datasets = response.datasets;
        updateOrderChart(order_chart, label, datasets);
    }

    function refresh_chart(response){
        let order_report = response.order_report;
        let order_price_report = response.order_price_report;
        let product_report = response.product_report;
        let new_user_report = response.new_user_report;
        let visitor_report = response.visitor_report;
        var metrics_data = []


       // orders_conf.data.labels = order_report.months;
        orders_conf.data.datasets[0].label = order_report.label;
        orders_conf.data.datasets[0].data = createDataList(order_report.data, order_report.months);
        metrics_data.push({label:'Orders', count: order_report.total_count})

        orders_price_conf.data.labels = order_price_report.months;
        orders_price_conf.data.datasets[0].label = order_price_report.label;
        orders_price_conf.data.datasets[0].data = order_price_report.data;

        products_conf.data.labels = product_report.months;
        products_conf.data.datasets[0].label = product_report.label;
        products_conf.data.datasets[0].data = product_report.data;
        metrics_data.push({label:'Products', count: product_report.total_count});

        new_users_conf.data.labels = new_user_report.months;
        new_users_conf.data.datasets[0].label = new_user_report.label;
        new_users_conf.data.datasets[0].data = new_user_report.data;
        metrics_data.push({label:'Users', count: new_user_report.total_count});

        metrics_data.push({label:'Visitors', count: visitor_report.total_visitors});
        metrics_data.push({label:'Unique Visitors', count: visitor_report.total_unique_visitors});
        metrics_data.push({label:'Facebook Visitors', count: visitor_report.total_facebook_visitors});
        metrics_data.push({label:'Suspicious Visitors', count: visitor_report.total_suspicious_visitors});
        
        visitor_conf.data.labels = visitor_report.months;
        visitor_conf.data.datasets[0] = {label:visitor_report.labels[0], data: visitor_report.data[0], backgroundColor: '#9b59b6'};

        unique_visitor_conf.data.labels = visitor_report.months;
        unique_visitor_conf.data.datasets[0] = {label:visitor_report.labels[3], data: visitor_report.data[3], backgroundColor: '#3498db'}

        facebook_visitor_conf.data.labels = visitor_report.months;
        facebook_visitor_conf.data.datasets[0] = {label:visitor_report.labels[1], data: visitor_report.data[1], backgroundColor: '#2ecc71'};

        suspicious_visitor_conf.data.labels = visitor_report.months;
        suspicious_visitor_conf.data.datasets[0] = {label:visitor_report.labels[2], data: visitor_report.data[2], backgroundColor: '#2c3e50'};


        visitors_conf.data.labels = visitor_report.months;
        var visitors_datasets = visitors_conf.data.datasets;
        if(visitors_datasets.length == 4){
            visitors_conf.data.datasets[0] = {label:visitor_report.labels[0], data: visitor_report.data[0], backgroundColor: '#9b59b6'};
            visitors_conf.data.datasets[1] = {label:visitor_report.labels[1], data: visitor_report.data[1], backgroundColor: '#2ecc71'};
            visitors_conf.data.datasets[2] = {label:visitor_report.labels[2], data: visitor_report.data[2], backgroundColor: '#2c3e50'};
            visitors_conf.data.datasets[3] = {label:visitor_report.labels[3], data: visitor_report.data[3], backgroundColor: '#3498db'};
            
        }else if (visitors_datasets.length == 1){
            visitors_conf.data.datasets[0] = {label:visitor_report.labels[0], data: visitor_report.data[0], backgroundColor: '#9b59b6'};
            visitors_conf.data.datasets.push({label:visitor_report.labels[1], data: visitor_report.data[1], backgroundColor: '#2ecc71'});
            visitors_conf.data.datasets.push({label:visitor_report.labels[2], data: visitor_report.data[2], backgroundColor: '#2c3e50'});
            visitors_conf.data.datasets.push({label:visitor_report.labels[3], data: visitor_report.data[3], backgroundColor: '#3498db'});
        }
        
        order_chart.update();
        product_chart.update();
        new_user_chart.update();
        order_price_chart.update();

        visitor_charts.update();
        unique_visitor_charts.update();
        facebook_visitor_charts.update();
        suspicious_visitor_charts.update();
        visitors_charts.update();

        updateMetrics(metrics_data);
    }


    function updateOrderChart(chart,label, datasets){
        var data = []
        datasets.forEach(dataset => {
            data[dataset.month - 1] = dataset.count;
        });
        chart.data.datasets[0].data = data;
        chart.update();
    }



    function addMetric(container, data){
        var el = $('<div/>').addClass('metric');
        $('<span/>').addClass('metric-title').html(data.label).appendTo(el);
        $('<span/>').addClass('metric-value').html(data.count).appendTo(el);
        container.append(el);

    }

    function addReportMetric(container, data){
        var el = $('<div/>').addClass('metric');
        $('<span/>').addClass('metric-title').html(data.label).appendTo(el);
        $('<span/>').addClass('metric-value').html(data.count).appendTo(el);
        container.append(el);

    }

    function updateMetrics(metrics_data){
        var container = $('#metrics');
        if(container.length == 0){
            console.error("No metrics container found.");
            return;
        }
        metrics_data.forEach(data =>{
            if (data.label == "Orders"){
                $('#metric-orders .metric-value', container).text(data.count);
            }else if(data.label == "Products"){
                $('#metric-products .metric-value', container).text(data.count);
            }else if(data.label == "Users"){
                $('#metric-users .metric-value', container).text(data.count);
            }else if(data.label == "Visitors"){
                $('#metric-visitors .metric-value', container).text(data.count);
            }else if(data.label == "Facebook Visitors"){
                $('#metric-facebook-visitors .metric-value', container).text(data.count);
            }else if(data.label == "Unique Visitors"){
                $('#metric-unique-visitors .metric-value', container).text(data.count);
            }else if(data.label == "Suspicious Visitors"){
                $('#metric-suspicious-visitors .metric-value', container).text(data.count);
            }
        });
    }

    function dashboardUpdate(){
        var options = {
            url:'/api/analytics/',
            type:'GET',
            data:{},
            dataType: 'json'
        }
        var promise = ajax(options).then(function(response){
            //report = response.report;
            refresh_chart(response);
            //updateMetrics(response)
        }, function(error){
            console.log("analytics fetch failed");
            console.log(error);
        });

    }
    $(document).ready(function(){
    console.log("analytics ready");
    //report = JSON.parse(JSON.parse(document.getElementById("report_script").textContent));
    Chart.platform.disableCSSInjection = true;
    Chart.defaults.global.elements.line.fill = false;
    Chart.defaults.global.elements.line.borderWidth = 2;

    var ctx_orders = $('#orders-diagram');
    var ctx_products = $('#products-diagram');
    var ctx_orders_prices = $('#orders-price-diagram');
    var ctx_new_users = $('#users-diagram');
    var ctx_visitor = $('#visitor-diagram');
    var ctx_unique_vistors_users = $('#unique-visitors-diagram');
    var ctx_facebook_vistors_users = $('#facebook-visitors-diagram');
    var ctx_visitors = $('#visitors-diagram');
    var ctx_suspicious_visitors = $('#suspicious-visitors-diagram');

    var empty_conf = {};
    order_chart = new Chart(ctx_orders, orders_conf);
    product_chart = new Chart(ctx_products, products_conf);
    order_price_chart = new Chart(ctx_orders_prices, orders_price_conf);
    new_user_chart = new Chart(ctx_new_users, new_users_conf);
    visitors_charts = new Chart(ctx_visitors, visitors_conf);
    visitor_charts = new Chart(ctx_visitor, visitor_conf);
    unique_visitor_charts = new Chart(ctx_unique_vistors_users, unique_visitor_conf);
    facebook_visitor_charts = new Chart(ctx_facebook_vistors_users, facebook_visitor_conf);
    suspicious_visitor_charts = new Chart(ctx_suspicious_visitors, suspicious_visitor_conf);
    dashboardUpdate();
    dashboardIntervalHandle = setInterval(dashboardUpdate, UPDATE_RATE); // 1000*60*1 = 1min
    });
});