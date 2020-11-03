function add_to_cart(product){
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-add-to-cart/',
        data : {product:product.id, quantity:product.quantity, csrfmiddlewaretoken: csrfmiddlewaretoken.val()}
    }
    add_promise = ajax(option).then(function(response){
        console.log("Product %s added into cart", product.name);
        //$("#cart-badge").text(response.count)
        document.getElementById('cart-badge').textContent = response.quantity;
    }, function(reason){
        console.error("Error on adding Product %s into cart", product.name);
        console.error(reason);
    });
}

function add_to_coupon(){
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]').val();
    var coupon = $('#coupon').val();
    if(coupon.length == 0 || csrfmiddlewaretoken.length == 0){
        console.error("invalid coupon");
        return;
    }
    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-add-coupon/',
        data : {coupon : coupon, csrfmiddlewaretoken : csrfmiddlewaretoken}
    }
    add_promise = ajax(option).then(function(response){
        console.log(response);
        document.getElementById('reduction').textContent = response.reduction;
        document.getElementById('total').textContent = response.total;
    }, function(reason){
        console.error("Error on adding Coupon \"%s\" to user cart", coupon);
        console.error(reason);
    });
}

function form_submit_add_cart(){
    var form = $('#add-cart-form');
    if(form.length < 0){
        console.log("No add to cart form found");
        return;
    }
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]', form);
    var data = {};
    var inputs = form.serializeArray();

    inputs.forEach(function(v,index){
        console.debug("name : %s - value : %s", v.name, v.value)
        data[v.name] = v.value;
    });    
    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-add-to-cart/',
        data : data
    }
    console.log("inputs : %s", inputs.length);
    console.log("data : ", data);
    console.log("option : ", option);
    
    add_promise = ajax(option).then(function(response){
        console.log("Product added into cart");
        console.log(response);
        //$("#cart-badge").text(response.count)
        document.getElementById('cart-badge').textContent = response.quantity;
    }, function(reason){
        console.error("Error on adding Product into cart");
        console.error(reason);
    });
    
}

function update_cart_item(item, to_update, plus_or_minus){
    console.log("updating item ", item);
    console.log("updating object ", to_update);
    console.log("Update action %s", plus_or_minus);
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
    var data = {};
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken.val();
    data['quantity'] = to_update['quantity'];
    data['action'] = to_update['action'];
    data['item'] = to_update['item_uuid'];

    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-cart-item/' + data['item'] + '/' + data['action'] + '/',
        data : data
    }
    add_promise = ajax(option).then(function(response){
        console.log(response);
        document.getElementById('cart-badge').textContent = response.count;
        if(parseInt(response['count']) == 0){
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
        //$("#cart-badge").text(response.count)
        
        
    }, function(reason){
        console.error("Error on updating cart item \"%s\"",data['item']);
        console.error("Error Response Text : \"%s\"", reason.responseText)
        console.error(reason);
    });
}

function update_cart_item_quantity(item_uuid, quantity, target){
    console.log("updating item ", item_uuid);
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
    var data = {};
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken.val();
    data['quantity'] = quantity;
    data['action'] = 'update';
    data['item_uuid'] = item_uuid;

    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-cart-item-update/',
        data : data
    }
    add_promise = ajax(option).then(function(response){
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
        document.getElementById('cart-badge').textContent = response['cart_quantity'];
        
    }, function(reason){

        console.error("Error on updating cart item \"%s\"",data['item_uuid']);
        console.error("Error Response Text : \"%s\"", reason.responseText)
        console.error(reason);
        target.val(reason.responseJSON['item_quantity']);
    });
}


$(document).ready(function(){
    $('#add-cart-form').submit(function(event){
        console.log("submiting cart form");
        event.preventDefault();
        form_submit_add_cart();
    });
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
        var plus_or_minus = item.data('action') == "increment";
        update_cart_item(item, obj, plus_or_minus);
    });
    $('.js-cart-item-quantity').on('keypress', function(e){
        if(e.which != 13){
            return;
        }
        var item = $(this);
        update_cart_item_quantity(item.data('item'), item.val(), item);
    });
    $('.js-add-coupon').on('click', add_to_coupon);
    $('.js-attr-select').on('click', function(event){
        var element = $(this);
        var input = $('#' + element.data('target'));
        input.val(element.data('value'));
        element.toggleClass('chips-selected', !element.hasClass('chips-selected')).siblings().removeClass('chips-selected');
    });
});