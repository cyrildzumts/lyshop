
define(['ajax_api', 'lang'], function(ajax_api, Locale) {
    'use strict';
    

    function Wishlist(){
        this.user = "";
        this.items = [];
        this.total = 0;
        this.csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]');

        console.log("Wishlist manager created");
    }

    Wishlist.prototype.init = function(){
        var wishlist_component = $('.wishlist-component');
        if(wishlist_component.length == 0){
            console.warn("no wishlist component found");
            return;
        }
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warn("no csrf_token found");
            return;
        }
        var self = this;

        $('.js-add-to-wishlist').on('click', function(){
            var item = $(this);
            
            var data = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken.value,
                'wishlist_uuid' : item.data('list'),
                'product_uuid' : item.data('product')
            }
            console.log("Adding new product to shop list with data : ", data);
            self.add(data, item.data('name'));
        });
        $('.js-remove-from-list').on('click', function(){
            var item = $(this);
            
            var data = {
                'csrfmiddlewaretoken': self.csrfmiddlewaretoken.value,
                'wishlist_uuid' : item.data('list'),
                'product_uuid' : item.data('product')
            }
            console.log("Adding new product to shop list with data : ", data);
            self.remove(data, item.data('name'), item.data('target'));
        });
        $(".js-create-shop-list").on('click', function(){
            var item = $(this);
            var target = $('#' + item.data('target'));
            $('#wishlist-create-error', target).text('');
            $('#name', target).val('');
            item.parent().hide();
            target.show();
        });
        $(".js-close-box-wrapper").on('click', function(){
            var item = $(this);
            var target = $('#' + item.data('target'));
            var target_show = $('#' + item.data('show'));
            target.hide();
            $('#wishlist-create-error', target).text('');
            $('#name', target).val('');
            target_show.show();
        });

        $('#add-wishlist-form').on('submit', function(event){
            event.stopPropagation();
            event.preventDefault();
            console.log("simulation shoplist creation ...");
            self.create_and_add($(this).serialize());
        });
        


        console.log("Wishlist initialized");
    }

    Wishlist.prototype.ui_update = function(){

    }

    Wishlist.prototype.rename = function(data, old_name){
        var self = this;
        if(!data){
            console.warn("No data for renaming wishlist");
            return;
        }
        console.log("Wishlist rename : Form Data : ", data);
        var option = {
            type:'POST',
            method: 'POST',
            dataType: 'json',
            url : '/wishlist/wishlists/ajax-rename-wishlist/',
            data : data
        }
        ajax_api(option, false).then(function(response){
            notify({level:'info', content: response.message});
        }, function(reason){
            console.error(reason);
            notify({level:'warn', content:'product could not be added'});
        });
    }

    Wishlist.prototype.create_and_add = function(data){
        var self = this;

        if(!data){
            console.warn("No data for to add to to wishlist");
            return;
        }
        console.log("Add To Wishlist : Form Data : ", data);
        var option = {
            type:'POST',
            method: 'POST',
            dataType: 'json',
            url : '/wishlist/wishlists/ajax-create-add-wishlist/',
            data : data
        }
        var wishlist_dialog = $('#wishlist-dialog');
        var input_name = $('#name', wishlist_dialog);
        var error_hint = $('#wishlist-create-error', wishlist_dialog);

        ajax_api(option, false).then(function(response){
            notify({level:'info', content: response.message});
            input_name.val('');
            wishlist_dialog.hide();
            error_hint.text('');
        }, function(reason){
            console.error(reason);
            error_hint.text(reason.responseJSON.message);
            notify({level:'warn', content:'product could not be added'});
        });
    }

    Wishlist.prototype.add = function(data, product_name){
        var self = this;
        if(!data){
            console.warn("No data for to add to to wishlist");
            return;
        }
        console.log("Add To Wishlist : Form Data : ", data);
        var option = {
            type:'POST',
            method: 'POST',
            dataType: 'json',
            url : '/wishlist/wishlists/ajax-add-to-wishlist/',
            data : data
        }
        var wishlist_dialog = $('#wishlist-dialog');
        ajax_api(option, false).then(function(response){
            notify({level:'info', content: response.message});
            wishlist_dialog.hide();
        }, function(reason){
            console.error(reason);
            notify({level:'warn', content:'product could not be added'});
        });
    }

    Wishlist.prototype.remove = function(data, product_name, target){
        var self = this;
        var p_target = $('#' + target);
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warning("Wishlist add oporation not allowed: csrf_token missing");
            return;
        }
        if(!data){
            console.warn("No data for to add to to wishlist");
            return;
        }
        console.log("Add To Wishlist Form Data : ", data);
        var option = {
            type:'POST',
            method: 'POST',
            dataType: 'json',
            url : '/wishlist/wishlists/ajax-remove-from-wishlist/',
            data : data
        }
        ajax_api(option, false).then(function(response){
            notify({level:'info', content: response.message});
            p_target.remove();
        }, function(reason){
            console.error(reason);
            notify({level:'warn', content:'product could not be added'});
        });
    }

    Wishlist.prototype.moveToAnotherList = function(list_uuid, product_uuid){
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warning("Wishlist add oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Puting product %s into wishlist", product_uuid);
    }

    Wishlist.prototype.clear = function(){
        if(!this.csrfmiddlewaretoken || !this.csrfmiddlewaretoken.value){
            console.warning("Wishlist add oporation not allowed: csrf_token missing");
            return;
        }
        console.log("Clearing Wishlist");
    }

    Wishlist.prototype.delete = function(data){

    }

    

    Wishlist.prototype.update_product = function(to_update){
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
            if(response.count == 0){
                document.location.reload();
                return ;
            }
            if(response['removed']){
                to_update.parent.fadeOut('slow').remove()
            }else{
                to_update.target.val(response['item_quantity']);
                to_update.update.html(response['item_total']);
            }
            $(".original-price").text(response.subtotal);
            $(".final-price").text(response.total);
            $(".js-cart-quantity").text(response.count);
            $(".js-cart-reduction").text(response.reduction);
            notify({level:'info', content:'cart updated'});
            //to_update.cart_total.html(response['cart_total']);
            //to_update.cart_quantity.html(response['count']);            
            
        }, function(reason){
            console.error("Error on updating cart item \"%s\"",data['item']);
            console.error("Error Response Text : \"%s\"", reason.responseText)
            console.error(reason);
        });
    }

    

    Wishlist.prototype.update_badge = function(quantity){
        $('.cart .badge').text(quantity);
    }

    return Wishlist;
});