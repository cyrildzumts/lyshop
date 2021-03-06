requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['attributes_api', 'ajax_api', 'components_api', 'commons', 'image_loader', 'accounts'], function(AttributeManager ,ajax_api, Component, accounts){
    console.log("DashboardApp loaded ...");
    var attr_manager = new AttributeManager();
    attr_manager.init();
    Component.initComponent();
    console.log("JQuery version :", $().jquery);
});