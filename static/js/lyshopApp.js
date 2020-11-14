requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'attributes_api', 'ajax_api', 'components_api'], function(Cart, AttributeManager ,ajax_api, Component){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    var attr_manager = new AttributeManager();
    cart.init();
    attr_manager.init();
    Component.initComponent();
    console.log("JQuery version :", $().jquery);
});