requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['cart_lyshop', 'attributes_api', 'ajax_api', 'components_api', 'checkout'], function(Cart, AttributeManager ,ajax_api, Component, Checkout){
    console.log("LyshopApp loaded ...");
    var cart = new Cart();
    var attr_manager = new AttributeManager();
    cart.init();
    attr_manager.init();
    Component.initComponent();
    var checkout = new Checkout(Component.tabs);
    checkout.init();
    console.log("JQuery version :", $().jquery);
});