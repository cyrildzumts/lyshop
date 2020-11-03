define(['ajax_api'], function(ajax_api) {
    'use strict';
    function Cart(){
        this.user = "cyrildz"
        this.items = [1,2,4,85,63];
        this.total = 25000;
        this.currency = "XAF";
        this.baseURL = "/cart/ajax-debug/";
        this.data_type = "json"

        console.log("New Cart created");
    }

    Cart.prototype.add = function(product_uuid){
        console.log("Adding product %s into cart", product_uuid);
        var csrf_token = document.querySelector('input[name="csrfmiddlewaretoken"]');
        
        var option = {
            type:'POST',
            dataType: this.data_type,
            url : this.baseURL,
            data : {product: product_uuid, csrfmiddlewaretoken:csrf_token.value}
        }
        ajax_api(option).then(
            (response)=>{
                console.log("ajax response : ", response);
            },
            (error)=>{
                console.log("ajax error : ", error);
            }
        );
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