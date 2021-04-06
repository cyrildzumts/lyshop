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
    var LI_PO_PREFIX = '#p-option-';
    var LI_PM_PREFIX = '#p-method-';
    var INPOUT_PM_PREFIX = '#pm-';
    var PAYMENT_METHOD_CONTAINER = "#payment-method ul";
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

    var PAY_AT_DELIVERY = 0;
    var PAY_AT_ORDER = 1;
    var PAY_WITH_PAY = 2;
    var PAY_BEFORE_DELIVERY = 3;

    var PAYMENT_OPTIONS = [PAY_AT_DELIVERY, PAY_AT_ORDER, PAY_WITH_PAY, PAY_BEFORE_DELIVERY];

    var ORDER_PAYMENT_CASH = 0;
    var ORDER_PAYMENT_PAY = 1;
    var ORDER_PAYMENT_MOBILE = 2;

    var PAYMENT_METHODS = [ORDER_PAYMENT_CASH, ORDER_PAYMENT_MOBILE, ORDER_PAYMENT_PAY];



    var PAYMENT_OPTION_METHODS_MAPPING = new Map();
    PAYMENT_OPTION_METHODS_MAPPING.set(PAY_AT_DELIVERY, [ORDER_PAYMENT_CASH]);
    PAYMENT_OPTION_METHODS_MAPPING.set(PAY_AT_ORDER, [PAY_WITH_PAY]);
    PAYMENT_OPTION_METHODS_MAPPING.set(PAY_BEFORE_DELIVERY, [ORDER_PAYMENT_CASH, ORDER_PAYMENT_MOBILE, ORDER_PAYMENT_PAY]);

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
        var addr = document.getElementById('address');
        $('.js-input-payment-option').on('change', function(event){
            self.payment_option = this.value;
            self.payment_method = -1;
            self.update_payment_method();
            self.validate_pament_options();
            console.log("payment option changed %s", this.value);
        });
        $('.js-input-payment-method').on('change', function(event){
            self.payment_method = $(this).data('mode');
            console.log("payment method changed : %s", this.value);
            self.validate_pament_method();
        });
        $('.js-add-address').on('click', function(){
            $('#new-address, #checkout-address').toggleClass('hidden');
            
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
        self.update_payment_method();
        tabs.init();
        
        $('input.js-input-ship-mode').prop('checked', false);
        $('.js-send').prop('disabled', true);
    };

    Checkout.prototype.validate_address = function(){
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
                    toggle = false;
                    break;
                }
            }
        }
        tabs.toggle_checked(address_tab, toggle);
    };
    Checkout.prototype.validate_pament_options = function(){
       var is_valid = PAYMENT_OPTIONS.includes(parseInt(this.payment_option));
       if(!is_valid){
           console.log("Payment Option is invalid");
       }
       //tabs.toggle_checked(payment_tab, is_valid);
       this.validate_pament_method();

    };

    Checkout.prototype.validate_pament_method = function(){
       var methods = PAYMENT_OPTION_METHODS_MAPPING.get(parseInt(this.payment_option));
       var is_valid = methods && methods.includes(parseInt(this.payment_method));
       if(!is_valid){
           console.log("Payment Method is invalid");
       }
        tabs.toggle_checked(payment_tab, is_valid);
        return is_valid;
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
        var add_promise = ajax(option, true).then(function(response){
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
        //this.payment_option = parseInt($('.js-input-payment-option').val());
        console.log("Checkout  update_payment_method :  option %s : type : %s ", this.payment_option, typeof this.payment_option);
        var methods = PAYMENT_OPTION_METHODS_MAPPING.get(parseInt(this.payment_option));
        var li_list = $(PAYMENT_METHOD_CONTAINER + " li");
        li_list.hide();
        $('input', li_list).each(function(){
            this.checked = false;
        });
        if(methods){
            methods.forEach(function(value, index){
                $(LI_PM_PREFIX + value, PAYMENT_METHOD_CONTAINER).show();
            });
        }
        
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