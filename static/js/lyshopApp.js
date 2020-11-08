requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'ajax_api','vendor/jquery.min'], function(Cart, ajax_api){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    //var attr_manager = new AttributeManager();
    cart.init();
    //attr_manager.init();
    console.log("JQuery version :", $().jquery);
});