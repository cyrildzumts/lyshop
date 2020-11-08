requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'ajax_api', 'attributes_api','vendor/jquery.min'], function(Cart, ajax_api, AttributeManager){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    var attribute_manager = new AttributeManager();
    cart.init();
    attribute_manager.init();
    console.log("JQuery version :", $().jquery);
});