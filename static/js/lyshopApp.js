requirejs.config({
    baseUrl :'static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'ajax', 'vendor/jquery-3.5.0.min'], function(Cart, ajax, $){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    console.log("JQuery version :", $().jquery);
});