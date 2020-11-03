define(['ajax_api', 'vendor/jquery.min'], function(ajax_api) {
    'use strict';
    function Cart(){
        this.user = "";
        this.items = [];
        this.total = 0;
        this.csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]');

        console.log("New Cart created");
    }

    Cart.prototype.init = function(){
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warn("no csrf_token found");
            return;
        }
        var self = this;

        $('.js-cart-update-item-quantity,.js-cart-delete-item').on('click', function(){
            var item = $(this);
            var obj = {};
            obj['action'] = item.data('action');
            obj['target'] = $('#' + item.data('target'));
            obj['update'] = $('#' + item.data('update'));
            obj['parent'] = $('#' + item.data('parent'));
            obj['cart_total'] = $('.js-cart-total');
            obj['cart_quantity'] = $('.js-cart-quantity');
            obj['item_uuid'] = item.data('item');
            self.update_product(obj);
        });

        $('#add-cart-form').submit(function(event){
            event.stopPropagation();
            event.preventDefault();
            self.add($(this).serialize());
        });
        $('.js-cart-item-quantity').on('keypress', function(e){
            if(e.which != 13){
                return;
            }
            var item = $(this);
            self.update_product_quantity(item.data('item'), item.val(), item);
        });
        $('.js-attr-select').on('click', function(event){
            var element = $(this);
            var input = $('#' + element.data('target'));
            input.val(element.data('value'));
            element.toggleClass('chips-selected', !element.hasClass('chips-selected')).siblings().removeClass('chips-selected');
        });
        $('.js-add-coupon').on('click', self.addCoupon.bind(this));
        $(".js-remove-coupon").on('click', self.removeCoupon);
        console.log("Cart initialized");
    }

    Cart.prototype.ui_update = function(){

    }


    Cart.prototype.add = function(data){
        var self = this;
        if(!data){
            console.warn("No data for to add to to cart");
            return;
        }
        var option = {
            type:'POST',
            dataType: 'json',
            url : '/cart/ajax-add-to-cart/',
            data : data
        }
        ajax_api(option).then(function(response){
            self.update_badge(response.quantity);
        }, function(reason){
            console.error(reason);
        });
    }

    Cart.prototype.remove = function(product){
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warning("Cart add oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Removing product from cart");
    }

    Cart.prototype.putInWishlist = function(product_uuid){
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warning("Cart add oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Puting product %s into wishlist", product_uuid);
    }

    Cart.prototype.clear = function(){
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warning("Cart add oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Clearing Cart");
    }

    Cart.prototype.addCoupon = function(){
        var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
        var coupon = $('#coupon').val();
        if(coupon.length == 0 || csrfmiddlewaretoken.length == 0){
            console.error("invalid coupon");
            return;
        }
        console.log("Cart addCoupon : this : ", this);
        this.isValidCoupon(coupon, function(response){
            $("#coupon-error").toggleClass('hidden', !response.valid);
            if(response.status && response.valid){
                
                var option = {
                    type:'POST',
                    dataType: 'json',
                    url : '/cart/ajax-add-coupon/',
                    data : {coupon : coupon, csrfmiddlewaretoken : csrfmiddlewaretoken}
                }
                ajax_api(option).then(function(data){
                    console.log(data);
                    document.getElementById('reduction').textContent = data.reduction;
                    document.getElementById('total').textContent = data.total;
                }, function(reason){
                    console.error("Error on adding Coupon \"%s\" to user cart", coupon);
                    console.error(reason);
                });
            }else if(response.status && !response.valid){
                $("#coupon-error").toggleClass('hidden', !response.valid);
                console.log("invalid coupon : %s", coupon);
            }
            
        });
    }
    

    Cart.prototype.removeCoupon = function(){
        var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
        if(!csrfmiddlewaretoken){
            console.warning("Cart remove oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Remove coupon %s from cart");
        var option = {
            type:'POST',
            dataType: 'json',
            url : '/cart/ajax-coupon-remove/',
            data : {csrfmiddlewaretoken : csrfmiddlewaretoken}
        }
        ajax_api(option).then(
            function(response){
                var data = JSON.parse(response);
                console.log(data);
                document.location.reload();
            }, 
            function(error){
                console.error("Error on vefirying Coupon");
            });

    }

    Cart.prototype.isValidCoupon = function(coupon, callback){
        var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
        if(!csrfmiddlewaretoken){
            console.warning("Cart add oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Verifying coupon ", coupon);
        var option = {
            type:'POST',
            dataType: 'json',
            url : '/cart/ajax-coupon-verify/',
            data : {coupon : coupon, csrfmiddlewaretoken : csrfmiddlewaretoken}
        }
        ajax_api(option).then(
            function(response){
                console.log(response);
                if(typeof callback == "function"){
                    callback(JSON.parse(response));
                }
            }, 
            function(error){
                console.error("Error on vefirying Coupon \"%s\" ", coupon);
                if(typeof callback == "function"){
                    callback(JSON.parse(error));
                }
            });
    }

    Cart.prototype.update_product = function(to_update){
        var self = this;
        var data = {};
        data['csrfmiddlewaretoken'] = this.csrfmiddlewaretoken.value;
        data['quantity'] = to_update['quantity'];
        data['action'] = to_update['action'];
        data['item'] = to_update['item_uuid'];

        var option = {
            type:'POST',
            dataType: 'json',
            url : '/cart/ajax-cart-item/' + data['item'] + '/' + data['action'] + '/',
            data : data
        }
        ajax_api(option).then(function(response){
            self.update_badge(response.count);
            if(parseInt(response.count) == 0){
                document.location.reload();
                return ;
            }
            if(response['removed']){
                to_update.parent.fadeOut('slow').remove()
            }else{
                to_update.target.val(response['item_quantity']);
                to_update.update.html(response['item_total'].replace('.', ','));
            }

            to_update.cart_total.html(response['cart_total'].replace('.', ','));
            to_update.cart_quantity.html(response['count']);            
            
        }, function(reason){
            console.error("Error on updating cart item \"%s\"",data['item']);
            console.error("Error Response Text : \"%s\"", reason.responseText)
            console.error(reason);
        });
    }

    Cart.prototype.update_product_quantity = function(item_uuid, quantity, target){
        console.log("updating item ", item_uuid);
        var data = {};
        data['csrfmiddlewaretoken'] = this.csrfmiddlewaretoken.value;
        data['quantity'] = quantity;
        data['action'] = 'update';
        data['item_uuid'] = item_uuid;
    
        var option = {
            type:'POST',
            dataType: 'json',
            url : '/cart/ajax-cart-item-update/',
            data : data
        }
        ajax_api(option).then(function(response){
            console.log(response);
    
            if(response['item_quantity'] == 0){
                $('#' + target.data('parent')).fadeOut('slow').remove();
            }else{
                target.val(response['item_quantity']);
                $('#' + target.data('total')).html(response['item_total'].replace('.', ','));
            }
    
            if(response['reduction']){
                $('#reduction').html(response['reduction'].replace('.', ','));
                $('#solded_price').html(response['solded_price'].replace('.', ','));
            }else{
                $('#reduction').html(response['reduction']);
            }
            
            $('#total').html(response['total'].replace('.', ','));
            $('.js-cart-quantity').html(response['cart_quantity']);
            this.update_badge(response['cart_quantity']);
            
        }, function(reason){
    
            console.error("Error on updating cart item \"%s\"",data['item_uuid']);
            console.error("Error Response Text : \"%s\"", reason.responseText)
            console.error(reason);
            target.val(reason.responseJSON['item_quantity']);
        });
    }

    Cart.prototype.update_badge = function(quantity){
        var badge = document.getElementById('cart-badge');
        if(badge){
            badge.textContent = quantity;
        }
    }

    return Cart
});