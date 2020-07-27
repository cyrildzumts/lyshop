


var order_chart;
var product_chart;
var request_chart;
var new_user_chart;
var analytics_label = 'Orders';
var analytics_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
var chart_type = 'line';
var orders_conf = {
    type : chart_type,
    data : {
        labels : [],
        datasets : [{
            label: '',
            data: []
        }],
    },
    options:{}
};
var products_conf = {
    type : chart_type,
    data : {
        labels : [],
        datasets : [{
            label: '',
            data: []
        }],
    },
    options:{}
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
    options:{}
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
    order_report = response.order_repor;
    product_report = response.product_report;
    new_user_report = response.new_user_report;

    orders_conf.data.labels = order_report.months;
    orders_conf.data.datasets[0].label = orders_conf.label;
    orders_conf.data.datasets[0].data = order_report.data;

    products_conf.data.labels = product_report.months;
    products_conf.data.datasets[0].label = product_report.label;
    products_conf.data.datasets[0].data = product_report.data;

    new_users_conf.data.labels = new_user_report.months;
    new_users_conf.data.datasets[0].label = new_user_report.label;
    new_users_conf.data.datasets[0].data = new_user_report.data;
    
    order_chart.update();
    product_chart.update();
    new_user_chart.update();
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
        report = response.report;
        refresh_chart(response);
        //updateMetrics(response)
    }, function(error){
        console.log("analytics fetch failed");
        console.log(error);
    });

}
$(document).ready(function(){
console.log("analytics ready");
report = JSON.parse(JSON.parse(document.getElementById("report_script").textContent));
Chart.defaults.global.elements.line.fill = false;
Chart.defaults.global.elements.line.borderWidth = 2;

var ctx_orders = $('#orders-diagram');
var ctx_products = $('#products-diagram');
//var ctx_requests = $('#payment-request-diagram');
var ctx_new_users = $('#users-diagram');

var empty_conf = {};
order_chart = new Chart(ctx_orders, orders_conf);
products_chart = new Chart(ctx_products, products_conf);
//requests_chart = new Chart(ctx_requests, requests_conf);
new_user_chart = new Chart(ctx_new_users, new_users_conf);
dashboardUpdate();
dashboardIntervalHandle = setInterval(dashboardUpdate,30000); // 1000*60*1 = 1min
});