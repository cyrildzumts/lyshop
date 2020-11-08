requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'ajax_api','vendor/jquery.min'], function(Cart, ajax_api){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    cart.init();
    console.log("JQuery version :", $().jquery);
});