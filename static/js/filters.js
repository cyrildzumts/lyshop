
var order_status_container;
var order_payment_option_container;
var order_status = [];
var filter_form;

function clean_form_before_submit(form){
    console.log("disabling empty fields");
    $('.filter-input', form).each(function(){
        this.disabled = this.value == "";
    });
    $('.no-submit', form).each(function(){
        this.disabled = true;
    });
}

function filter_singular_init(field_id, chips_class){
    var input = $(field_id);
    var selected_chips = $(chips_class);
    var values = ""
    selected_chips.each(function(index, element){
        var chips = $(this);
        if(index < selected_chips.length - 1){
            values += chips.data('value') + ",";
        }else{
            values += chips.data('value');
        }
    });
    input.val(values);
}

function initialize_filters(){
    filter_singular_init('#order-status-input', '.order-status-chips.chips-selected');
    filter_singular_init('#order-payment-option-input', '.order-payment-option-chips.chips-selected');
}


function integer_field_filter(element){
    var values = "";
    var input_target = $('#' + element.data('target'));
    var filter_type = element.data('type');
    var parent = element.parent();
    if (filter_type == "selection"){
        
        var selected_chips = $('.chips-selected', parent);
        selected_chips.each(function(index, element){
            var chips = $(this);
            if(index < selected_chips.length - 1){
                values += chips.data('value') + ",";
            }else{
                values += chips.data('value');
            }
        });
        element.toggleClass('chips-selected', !element.hasClass('chips-selected'));

    }else if(filter_type == "range-start"){
        var start;
        var end;
        if(element.hasClass('filter-input-start')){
            start = element.val();
            end = $('#' + element.data('range-next')).val();
        }else if(element.hasClass('filter-input-end')){
            end = element.val();
            start = $('#' + element.data('range-next')).val();
        }
        values = start + '-' + end;

    }else if (filter_type == "value"){
        values = element.val();
    }
    input_target.val(values);

}

function install_integer_filter(){
    $('.js-list-filter').on('click', function(){
        integer_field_filter($(this));
    });
    $('.js-range-filter, .js-value-filter').on('keyup,change', function(){
        integer_field_filter($(this));
    });
    /*
    $('.js-value-filter').on('keyup,change', function(){
        integer_field_filter($(this));
    });
    */
}

function toggle_order_status(element){
    var value = element.data('value');
    var added = false;
    var status_input = $('#order-status-input');
    var current_value = status_input.val();
    var values = ""
    element.toggleClass('chips-selected', !element.hasClass('chips-selected'));
    var selected_chips = $('.order-status-chips.chips-selected');
    selected_chips.each(function(index, element){
        var chips = $(this);
        if(index < selected_chips.length - 1){
            values += chips.data('value') + ",";
        }else{
            values += chips.data('value');
        }
        added = true;
    });
    console.log("Order status values : %s", values);
    status_input.val(values);
    return added;
}

function toggle_playment_option(element){
    var value = element.data('value');
    var added = false;
    var input = $('#order-payment-option-input');
    var current_value = input.val();
    var values = ""
    element.toggleClass('chips-selected', !element.hasClass('chips-selected'));
    var selected_chips = $('.order-payment-option-chips.chips-selected');
    selected_chips.each(function(index, element){
        var chips = $(this);
        if(index < selected_chips.length - 1){
            values += chips.data('value') + ",";
        }else{
            values += chips.data('value');
        }
        added = true;
    });
    input.val(values);
    return added;
}


function toggle_amount_option(element){
    var input = $('#amount-filter');
    var filter_action = element.data('value');
    var added = false;
    console.log("updating amount filter");
    console.log("Filter action : %s", filter_action);
    if(input.val() == filter_action){
        //element.removeClass('chips-selected').siblings().removeClass('chips-selected');
        input.val('');
    }else{
        input.val(filter_action);
        added = true;
        //element.addClass('chips-selected').siblings().removeClass('chips-selected');
    }
    console.log("#amount-filter : %s", input.val());
    console.log("#amount-input  : %s", $('#amount-input').val())
    $(".amount-filter-chips .chips").removeClass('chips-selected');
    return added;
}

function toggle_date_filter(element){
    var input = $('#filter-action');
    var filter_action = element.data('filter-action');
    if(input.val() == filter_action){
        element.removeClass('chips-selected').siblings().removeClass('chips-selected');;
        input.val('');
    }else{
        input.val(filter_action);
        element.addClass('chips-selected').siblings().removeClass('chips-selected');
    }
}


function integer_filter(){
    
}
function date_filter(){

}

$(document).ready(function(){
    filter_form = $('#filter-form');
    $('#filter-form').on('submit', function(event){
        console.log("Filter form submition");
        clean_form_before_submit(this);
    });
    $('.js-pagination').on('click', function(event){
        
        if(filter_form.length != 0){
            event.preventDefault();
            event.stopPropagation();
            
            var page = $(event.target).data('page');
            var input = $('<input />', {
                name : 'page',
                value : page
            });
            input.appendTo(filter_form);
            console.log('form serialize : \"%s\"', $('.filter-input').not('[value=""]').serialize());
            console.log("Added page input to filter form", input);
            filter_form.submit();
        }
        

    });

    $("#amount-filter-input").on('keyup', function(event){
        var input = $(this);
        $(input.data('update')).text(input.val());
        $("#" + input.data('target')).val(input.val());
    });
    initialize_filters();
    install_integer_filter();
    /*
    $('.js-list-filter').on('click', function(){
        var element = $(this);
        var name = element.data('name');
        var added = false;
        if(name == 'order-status'){
            added = toggle_order_status(element);
            
        }else if(name == 'payment-option'){
            added = toggle_playment_option(element);
            
        }else if(name == 'amount'){
            added = toggle_amount_option(element);
            element.toggleClass("chips-selected", added);
        }else if(name == 'created_at'){
            added = toggle_date_filter(element);
            element.toggleClass("chips-selected", added);
        }
        
        
    });
    */
    console.log("Filter module ready");
});