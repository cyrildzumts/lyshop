
define(['vendor/Chart.min', 'ajax_api'],
function(Chart, ajax){
    'use strict';
    var dashboardIntervalHandle;
    var order_chart;
    var product_chart;
    var visitors_charts;
    var visitor_charts;
    var unique_visitor_charts;
    var facebook_visitor_charts;
    var order_price_chart;
    var new_user_chart;
    var analytics_label = 'Orders';
    var analytics_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    var chart_type = 'bar';
    var UPDATE_RATE = 15000;
    var default_scales = {
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
                    labelString : "Count"
                }
            }
        ]
    }
    var orders_conf = {
        type : chart_type,
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
        type : chart_type,
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
        type : chart_type,
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
        type : chart_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Visitors',
                data: [],
                backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var visitor_conf = {
        type : chart_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Visitors',
                data: [],
                backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var unique_visitor_conf = {
        type : chart_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Unique Visitors',
                data: [],
                backgroundColor : "#D2AE00"
            }],
        },
        options:{
            scales : default_scales
        }
    };

    var facebook_visitor_conf = {
        type : chart_type,
        data : {
            labels : [],
            datasets : [{
                label: 'Facebook Visitors',
                data: [],
                backgroundColor : "#D2AE00"
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
        console.log("Dispatching chart update to \"%s\"",label);
        updateOrderChart(order_chart, label, datasets);
    }

    function refresh_chart(response){
        let order_report = response.order_report;
        let order_price_report = response.order_price_report;
        let product_report = response.product_report;
        let new_user_report = response.new_user_report;
        let visitor_report = response.visitor_report;


        orders_conf.data.labels = order_report.months;
        orders_conf.data.datasets[0].label = order_report.label;
        orders_conf.data.datasets[0].data = order_report.data;

        orders_price_conf.data.labels = order_price_report.months;
        orders_price_conf.data.datasets[0].label = order_price_report.label;
        orders_price_conf.data.datasets[0].data = order_price_report.data;

        products_conf.data.labels = product_report.months;
        products_conf.data.datasets[0].label = product_report.label;
        products_conf.data.datasets[0].data = product_report.data;

        new_users_conf.data.labels = new_user_report.months;
        new_users_conf.data.datasets[0].label = new_user_report.label;
        new_users_conf.data.datasets[0].data = new_user_report.data;

        visitor_conf.data.labels = visitor_report.months;
        visitor_conf.data.datasets[0] = visitor_report.data[0];

        unique_visitor_conf.data.labels = visitor_report.months;
        unique_visitor_conf.data.datasets[0] = visitor_report.data[1];

        facebook_visitor_conf.data.labels = visitor_report.months;
        facebook_visitor_conf.data.datasets[0] = visitor_report.data[2];


        visitors_conf.data.labels = visitor_report.months;
        var visitors_datasets = visitors_conf.data.datasets;
        if(visitors_datasets.length == 3){
            visitors_conf.data.datasets[0] = {label:visitor_report.labels[0], data: visitor_report.data[0]};
            visitors_conf.data.datasets[1] = {label:visitor_report.labels[1], data: visitor_report.data[1]};
            visitors_conf.data.datasets[2] = {label:visitor_report.labels[2], data: visitor_report.data[2]};
        }else if (visitors_datasets.length == 1){
            visitors_conf.data.datasets[0] = {label:visitor_report.labels[0], data: visitor_report.data[0]};
            visitors_conf.data.datasets.push({label:visitor_report.labels[1], data: visitor_report.data[1]});
            visitors_conf.data.datasets.push({label:visitor_report.labels[2], data: visitor_report.data[2]});
        }
        

        //visitors_conf.data.datasets[1].label = visitor_report.labels[1];
        //visitors_conf.data.datasets[1] = visitor_report.data[1];

        //visitors_conf.data.datasets[2].label = visitor_report.labels[2];
        //visitors_conf.data.datasets[2] = visitor_report.data[2];
        
        order_chart.update();
        product_chart.update();
        new_user_chart.update();
        order_price_chart.update();

        visitor_charts.update();
        unique_visitor_charts.update();
        facebook_visitor_charts.update();
        visitors_charts.update();
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
            if(data.label == "Vouchers"){
                $('#vouchers .metric-value .sold', container).text(data.sold);
                $('#vouchers .metric-value .total', container).text(data.count);
            }else if (data.label == "Orders"){
                $('#orders .metric-value', container).text(data.count);
            }else if(data.label == "Products"){
                $('#products .metric-value', container).text(data.count);
            }else if(data.label == "Payment Requests"){
                $('#p_requests .metric-value', container).text(data.count);
            }else if(data.label == "Users"){
                $('#users .metric-value', container).text(data.count);
            }else if(data.label == "Services"){
                $('#services .metric-value', container).text(data.count);
            }else{
                console.error("Metrics Error: no target found for label %s.", data.label);
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
            console.log("analytics fetch succeed");
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
    var ctx_unique_vistors_users = $('#unique_vistors-diagram');
    var ctx_facebook_vistors_users = $('#facebook_vistors-diagram');
    var ctx_visitors = $('#visitors-diagram');

    var empty_conf = {};
    order_chart = new Chart(ctx_orders, orders_conf);
    product_chart = new Chart(ctx_products, products_conf);
    order_price_chart = new Chart(ctx_orders_prices, orders_price_conf);
    new_user_chart = new Chart(ctx_new_users, new_users_conf);
    visitors_charts = new Chart(ctx_visitors, visitors_conf);
    visitor_charts = new Chart(ctx_visitor, visitor_conf);
    unique_visitor_charts = new Chart(ctx_unique_vistors_users, unique_visitor_conf);
    facebook_visitor_charts = new Chart(ctx_facebook_vistors_users, facebook_visitor_conf);
    dashboardUpdate();
    dashboardIntervalHandle = setInterval(dashboardUpdate, UPDATE_RATE); // 1000*60*1 = 1min
    });
});