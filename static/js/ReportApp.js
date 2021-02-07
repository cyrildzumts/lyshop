requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['ajax_api','components_api', 'commons' ,'analytics'], function(ajax_api, Component){
    console.log("ReportApp loaded ...");
    Component.initComponent();
    console.log("JQuery version :", $().jquery);
});