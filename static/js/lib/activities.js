define(['vendor/js.cookie', 'ajax_api'],function(Cookies, ajax_api) {
    'use strict';
    var user_session_key = "sessionid";
    var user_ref_key = "user_ref";
    const update_delay = 60000;
    var timer ;
    var csrfmiddlewaretoken = document.querySelector('input[name="csrfmiddlewaretoken"]');

    var user_session = Cookies.get(user_session_key);
    var user_ref = Cookies.get(user_ref);
    var option = {
        type:'POST',
        method: 'POST',
        dataType: 'json',
        url : '/api/update-activity/',
        data : {'sessionid': user_session, 'user_ref': user_ref, 'csrfmiddlewaretoken': csrfmiddlewaretoken.value}
    }

    function update_user_activity(){
        ajax_api(option).then(function(response){
            console.info(response)
        }, function(reason){
            console.warn(reason);
        });
    }
    function user_active(){
        clearTimeout(timer);
        timer = setTimeout(update_user_activity, update_delay);
    }


    if(window){
        window.onload = user_active;
        window.onkeypress = user_active;
        window.onclick = user_active;
        window.onscroll = user_active;
        window.onmousedown = user_active;
    }
    
    console.log("activies.js installed");
    user_active();
});