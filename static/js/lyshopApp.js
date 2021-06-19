requirejs.config({
    baseUrl :'/static/js/lib',
    paths:{
        vendor: '../vendor'
    }
});

requirejs(['accounts','cart_lyshop', 'attributes_api', 'ajax_api', 'components_api', 'checkout','wishlist', 'commons', 'image_loader', 'activities'], function(account, Cart, AttributeManager ,ajax_api, Component, Checkout, Wishlist){
    console.log("LyshopApp loaded ...");
    account.init();
    var cart = new Cart();
    var wishlist = new Wishlist();
    var attr_manager = new AttributeManager();
    cart.init();
    cart.set_user(account.get_user());
    wishlist.init();
    attr_manager.init();
    Component.initComponent();
    var checkout = new Checkout(Component.tabs);
    checkout.init();
    console.log("JQuery version :", $().jquery);
});