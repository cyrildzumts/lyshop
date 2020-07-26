


var order_chart;
var products_chart;
var requests_chart;
var user_chart;
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

function refresh_chart(response_report){
    orders_conf.data.labels = response_report.months;
    orders_conf.data.datasets[0].label = response_report.label;
    orders_conf.data.datasets[0].data = response_report.data;
    order_chart.update();
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
        report = response.report;
        refresh_chart(response.report);
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
var ctx_users = $('#users-diagram');
/*
orders_conf = {
    type : chart_type,
    data : {
        labels : report.months,
        datasets : [{
            label: report.label,
            data: report.data
        }],
    },
    options:{}
};
*/
var products_conf = {
    type : chart_type,
    data : {
        labels : analytics_labels,
        datasets : [{
            label: 'Products',
            data: []
        }],
    },
    options:{}
};
/*
var requests_conf = {
    type : chart_type,
    data : {
        labels : analytics_labels,
        datasets : [{
            label: 'Payment Requests',
            data: []
        }],
    },
    options:{}
};
*/
var users_conf = {
    type : chart_type,
    data : {
        labels : analytics_labels,
        datasets : [{
            label: 'Users Online',
            data: []
        }],
    },
    options:{}
};
var empty_conf = {};
order_chart = new Chart(ctx_orders, orders_conf);
//products_chart = new Chart(ctx_products, products_conf);
//requests_chart = new Chart(ctx_requests, requests_conf);
//user_chart = new Chart(ctx_users, users_conf);
dashboardUpdate();
dashboardIntervalHandle = setInterval(dashboardUpdate,30000); // 1000*60*1 = 1min
});