define([
'ajax_api'
], function(ajax) {
    'use strict';
    var ADDRESS_FIELDS = [ 
            'user', 'city', 'firstname', 'lastname', 'country', 
            'postal_code','phone_number', 'address_extra', 'street',
            'house_number', 'is_active'
        ];

    var ADDRESS_FIELDS_REQUIRED = [ 
        'user', 'city', 'firstname', 'lastname', 'country', 
        'postal_code','phone_number', 'street'
 
    ];
    var SHIP_STANDARD = 0;
    var SHIP_EXPRESS  = 1
    var SHIP_IN_STORE = 2
    var SHIP_IN_STORE_POG = 3
    var SHIP_IN_STORE_LBV = 4
    var SHIPPING_ADDRESS_CONTAINER = "address-container";
    var api_address_url = '/api/create-address/';
    var address = {
        id : "",
        name : "",
        email : "",
        city : "",
        postal_code: "",
        street : "",
        house_number : "",
        phone_number : "",
        country : ""
    };
    var step = {
        index : 1,
        valid : false,
        tab : null
    };
    var address_tab = 1;
    var payment_tab = 2;
    var verification_tab = 3;
    var tabs = null;

    var Checkout = function(tabs_comp){
        tabs = tabs_comp;
        this.address = {};
        this.payment_option = -1;
        this.payment_method = -1;
        this.currentTab = 1;
        this.shipping_price = 0;
        this.items_count = 0;
        this.steps = [];
        this.current_step = {};
        
    };
    
    Checkout.prototype.init = function(){
        var self = this;
        $('.js-input-payment-option').on('change', function(event){
            console.log("%s =  %s - checked : %s",this.name, this.value, this.checked);
            self.payment_option = this.value;
            self.validate_pament_options();
        });
        $('.js-input-payment-method').on('change', function(event){
            console.log("%s =  %s - checked : %s",this.name, this.value, this.checked);
            self.payment_method = this.value;
            self.validate_pament_options();
        });
        $('.js-add-address').on('click', function(){
            $('#new-address, #checkout-address').toggleClass('hidden');
            var addr = document.getElementById('address');
            if(addr){
                addr.toggleAttribute('disabled');
            }
            
        });
        $('.js-create-address').on('click', function(){
            self.create_address();
        });
        $('.js-input-ship-mode').on('change', function(event){
            self.ship_mode_changed(this);
        });
        this.validate_address();
        tabs.init();
        $('input.js-input-ship-mode').prop('checked', false);
        console.log("Checkout initialized");
    };

    Checkout.prototype.validate_address = function(){
        console.log("Validating Address : ");
        var toggle = false;
        var address_input = $('#address').get();
        var inputs_container = $('#new-address').get();
        if(address_input){
            toggle = true;
        }else if(inputs_container){
            var inputs = $("input", inputs_container);
            toggle = true;
            var i;
            for(i in inputs){
                if(i.value == ""){
                    console.log("%s : %s", i.name, i.value);
                    toggle = false;
                    break;
                }
            }
        }
        tabs.toggle_checked(address_tab, toggle);
    };
    Checkout.prototype.validate_pament_options = function(){
       console.log("Validatin Payment Options : ");
       console.log("payment_option : %s - payment_method : %s ", this.payment_option, this.payment_method);
       var toggle = false;
       if(this.payment_method == -1 || this.payment_option == -1){
           console.log("Payment Options are invalid");
       }else{
           toggle = true;
       }
       tabs.toggle_checked(payment_tab, toggle);

    };

    Checkout.prototype.create_address = function(){
        var self = this;
        var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
        var container = $('#new-address');
        var address_inputs = $('input', container);
        var available_fields = [];
        var data = {
            'csrfmiddlewaretoken' : csrfmiddlewaretoken.val()
        };
        address_inputs.each(function(){
            if(this.value){
                available_fields.push(this.name);
            }
            data[this.name] = this.value;
        });
        var missing_fields = ADDRESS_FIELDS_REQUIRED.filter(field => !available_fields.includes(field));
        if(missing_fields.length > 0){
            missing_fields.forEach(field =>{
                console.error("Address required field %s is missing", field);
                $(`input[name="${field}"]`, container).addClass('warn');
            });
            return;
        }else{
            address_inputs.removeClass('warn');
        }
        var option = {
            type:'POST',
            dataType: 'json',
            url : api_address_url,
            data : data
        }
        var add_promise = ajax(option).then(function(response){
            console.log("Address Created : %s", response['status']);
            console.log(response);
            if(response.status){
                address_inputs.each(function(){
                    this.disabled = 'disabled';
                });
                var input = $('<input>', {name : 'address', type :'hidden', value : response.id});
                input.appendTo(container);
                tabs.toggle_checked(address_tab, true);
                $('.js-add-address, .js-create-address').addClass('disabled').prop('disabled', 'disabled');
            }else{
                console.log("address not created. Error : %s", response.error);
            }
            
        }, function(reason){
            console.error("Error on adding Product into cart");
            console.error(reason);
        });
    }

    Checkout.prototype.validate_cart = function(){

    };

    Checkout.prototype.update_payment_option = function(){

    };
    Checkout.prototype.update_payment_method = function(){
        
    };
    Checkout.prototype.ship_mode_changed = function(el){
        var mode = parseInt($(el).data('mode'));
        var shipping_price_el = $('.js-shipping-price');
        var grand_total_el = $('.js-grand-total');
        var total_el = $('.js-final-price');
        var total = parseInt(total_el.text());
        var shipping_price = parseInt($(el).data('price'));
        total += shipping_price;
        shipping_price_el.text(shipping_price);
        grand_total_el.text(total);
        var show_address_container = mode == SHIP_EXPRESS || mode == SHIP_STANDARD;
        $("#" + SHIPPING_ADDRESS_CONTAINER).toggleClass('hidden', !show_address_container)
    };
    
    return Checkout;
    
});