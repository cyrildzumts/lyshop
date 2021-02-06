requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['ajax_api', 'analytics'], function(ajax_api){
    console.log("ReportApp loaded ...");
    console.log("JQuery version :", $().jquery);
});