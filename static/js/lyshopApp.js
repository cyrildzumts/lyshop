requirejs.config({
    baseUrl :'js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'ajax', 'vendor/jquery.min'], function(Cart, ajax, LS){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    console.log("JQuery version : %s", LS().jquery);
});