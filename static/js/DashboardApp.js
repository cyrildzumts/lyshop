
requirejs(['ajax_api', 'attributes_api','vendor/jquery.min'], function(ajax_api, AttributeManager){
    console.log("DashboardApp loaded ...");
    var attribute_manager = new AttributeManager();
    attribute_manager.init();
    console.log("JQuery version :", $().jquery);
});