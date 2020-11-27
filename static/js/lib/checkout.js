define([
'ajax_api'
], function(ajax_api) {
    'use strict';
    var ADDRESS_FIELDS = [ 
            'user', 'city', 'firstname', 'lastname', 'country', 
            'postal_code','phone_number', 'address_extra', 'street',
            'house_number', 'is_active'
        ];
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
        });
        $('.js-create-address').on('click', function(){
            self.create_address();
        });
        this.validate_address();
        tabs.init();
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
        var data = {
            'csrfmiddlewaretoken' : csrfmiddlewaretoken.val()
        };
        address_inputs.each(function(){
            data[this.name] = this.value;
        });
        $('#checkout-address').prop('disabled', true);
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
                    this.disabled = true;
                });
                var input = $('<input>', {name : 'address', type :'hidden', value : response.id});
                input.appendTo(container);
                tabs.toggle_checked(address_tab, true);
                $('.js-add-address, .js-create-address').prop('disabled', true);

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
    
    return Checkout;
    
});