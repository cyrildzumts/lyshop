var query_delay = 800;
var scheduled_query = false;
var $user_search_result = undefined;
var $user_search_target = undefined;
var $user_search_target_name = undefined;

function account_form_validation(){
    console.log("Account form validation not implemented yet.")
    return true;
}


function activate_editable_inputs(context){
    console.debug("activating editableinputs");
    var $editable_inputs = $('input.js-editable', context);
    $editable_inputs.addClass('editable').prop('disabled', false);

}

function deactivate_editable_inputs(context){
    console.debug("deactivating editableinputs");
    var $editable_inputs = $('input.js-editable', context);
    $editable_inputs.removeClass('editable').prop('disabled', true);;
}


function init(){
    var $editable_inputs = $('input.js-editable');
    $editable_inputs.removeClass('editable').prop('disabled', true);;
    $('#form-controls').hide();
}


var userSearch = function(options){

    var promise = ajax(options).then(function(response){
        //console.log("User Search succeed");
        //console.log(response);
        $user_search_result.empty();
        response.forEach(function(user, index){
            var full_name = user.first_name + " " +  user.last_name;
            $('<li>').data('user-id', user.id).data('user-name', full_name).html(full_name + " [" + user.username + "]").
            on('click', function(event){
                event.stopPropagation();
                var user_id = $(this).data('user-id');
                var user_name = $(this).data('user-name');
                $user_search_target.val(user_id);
                //$(".js-user-search").val(user_name);
                $user_search_target_name.val(user_name);
                $user_search_result.hide();
                $user_search_result.empty();
            }).appendTo($user_search_result);
            $user_search_result.show();
        });

    }, function(error){
        console.log("User Search failed");
        console.log(error);
    });
}




$(document).ready(function(){
    init();
    $user_search_result = $('#user-search-result');
    $user_search_target = $($user_search_result.data('target'));
    $user_search_target_name = $($user_search_result.data('target-name'));
    
    $('.js-edit-form').on('click', function(event){
        var ctx = $($(this).data('target'));
        $(this).addClass('disabled');
        activate_editable_inputs(ctx);
        $('#form-controls').show();
    });

    $('.js-form-edit-cancel').on('click', function(event){
        event.preventDefault();
        var ctx = $($(this).data('target'));
        var hide_el = $($(this).data('hide'));
        hide_el.hide();
        $('.js-edit-form').removeClass('disabled');
        deactivate_editable_inputs(ctx);
    });
    
    
    $('.js-user-search').on('keyup', function(event){
        event.stopPropagation();
        var query = $(this).val();
        query = query.trim()
        if(query.length == 0 ){
            return;
        }
        var options = {
            url:'/api/user-search/',
            type: 'GET',
            data : {'search': query},
            dataType: 'json'
        };
        if(scheduled_query){
            clearTimeout(scheduled_query);
        }
        scheduled_query = setTimeout(userSearch, query_delay, options);
    });
});