requirejs.config({
    baseUrl :'static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'ajax_api', 'vendor/jquery.min'], function(Cart, ajax_api){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    console.log("JQuery version :", $().jquery);
    cart.add("457g78-bbgghd-45877f788f-der455tg");
});