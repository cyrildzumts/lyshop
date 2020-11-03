define(['ajax_api'], function(ajax_api) {
    'use strict';
    function Cart(){
        this.user = "cyrildz"
        this.items = [1,2,4,85,63];
        this.total = 25000;
        this.currency = "XAF";
        console.log("New Cart created");
    }

    Cart.prototype.add = function(product_uuid){
        console.log("Adding product %s into cart", product_uuid);
    }
    Cart.prototype.remove = function(product_uuid){
        console.log("Removing product %s from cart", product_uuid);
    }

    Cart.prototype.putInWishlist = function(product_uuid){
        console.log("Puting product %s into wishlist", product_uuid);
    }

    Cart.prototype.clear = function(){
        console.log("Clearing Cart");
    }

    Cart.prototype.addCoupon = function(coupon){
        console.log("Adding coupon %s into cart", coupon);
    }

    Cart.prototype.removeCoupon = function(coupon){
        console.log("Remove coupon %s from cart", coupon);
    }

    Cart.prototype.isValidCoupon = function(coupon){
        console.log("Verifying coupon ", coupon);
    }

    return Cart
});