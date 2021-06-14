define([
    'ajax_api',
], function(ajax_api) {
    'use strict';
    var user = {};
    var user_available = false;
    var query_delay = 800;
    var scheduled_query = false;
    var $user_search_result = undefined;
    var $user_search_target = undefined;
    var $user_search_target_name = undefined;
    var query = "";
    var options = {
        url:'/api/current-user/',
        type: 'GET',
        data : {},
        dataType: 'json'
    };
    var search_options = {
        url:'/api/user-search/',
        type: 'GET',
        data : {'search': query},
        dataType: 'json'
    };

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


    function userSearch(options){

        ajax_api.ajax(options).then(function(response){
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

    function init(){
        $user_search_result = $('#user-search-result');
        $user_search_target = $($user_search_result.data('target'));
        $user_search_target_name = $($user_search_result.data('target-name'));
        var $editable_inputs = $('input.js-editable');
        $editable_inputs.removeClass('editable').prop('disabled', true);;
        $('#form-controls').hide();
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
            query = $(this).val().trim();
            if(query.length == 0 ){
                return;
            }
            search_options.data.search = query
            if(scheduled_query){
                clearTimeout(scheduled_query);
            }
            scheduled_query = setTimeout(userSearch, query_delay, search_options);
        });
        if(!user_available){
            ajax_api.ajax(options).then(function(response){
                user = response;
                user_available = true;
                console.log("current user : ", response);
                console.log("account module initialised for user : ", user)
            }, function(error){
                user_available = false;
            });
        }
        
    }

    init();


    return {
        get_username : function(){
            
            return user_available ?  user.username : "";
        },
        get_last_login : function(){
            return user_available ?  user.last_login : "";
        },

        get_user_id : function(){
            return user_available ?  user.user_id : -1;
        },
        is_initialised : function(){
            return user_available;
        }
    }
    
});

