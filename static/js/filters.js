
var order_status_container;
var order_payment_option_container;
var order_status = [];


function toggle_order_status(element){
    var value = element.data('value');
    var added = false;
    var status_list = $('option', order_status_container).filter(function(index, el){
        return el.value == value;
    });
    if(status_list.length == 0){
        order_status_container.append($('<option/>', {
            value: value,
            selected : true
        }));
        added = true;
    }else{
        $('option', order_status_container).each(function(){
            if(this.value == value){
                $(this).remove();
            }
        });
    }
    return added;
}

function toggle_playment_option(element){
    var value = element.data('value');

    var added = false;
    var payment_option_list = $('option', order_payment_option_container).filter(function(index, el){
        return el.value == value;
    });
    if(payment_option_list.length == 0){
        order_payment_option_container.append($('<option/>', {
            value: value,
            selected : true
        }));
        added = true;
    }else{
        $('option', order_payment_option_container).each(function(){
            if(this.value == value){
                $(this).remove();
            }
        });
    }
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

function order_amount_filter(){

}
function order_status_filter(){
    
}
function order_payment_option_filter(){

}
function integer_filter(){
    
}
function date_filter(){

}