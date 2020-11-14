
var Notification = (function(){
    function Notification(){
        this.messages = {};
        this.notifications = {};
    }

    Notification.prototype.init = function(){
        console.log("Notification initialized");
        this.notifications = $('.notification-list');
        if(this.notifications.length > 0){
            console.log("Notification found");
            $(this.notifications.data('toggle')).show();
        }
    };

    return Notification;
})();



var isDirty = false;

function can_leave(){
    isDirty = false;
    //window.onbeforeunload = null;
}

function askConfirmation(event){
    var ret = undefined;
    if(isDirty){
        if(event){
            event.preventDefault();
            event.returnValue = "You have unsubmitted data. Leaving this page will lost the data."
        }
        ret =  "You have unsubmitted data. Leaving this page will lost the data.";
    }else{
        delete event['returnValue'];
    }
    
    return ret;
}

function prevent_leaving(){
    isDirty = true;
    //window.onbeforeunload = onbeforeunload;
}

$(document).ready(function(){

let tabs = new Tabs();
tabs.init();

var modal = new Modal({});

//$(window).on('beforeunload', onbeforeunload);
window.addEventListener('beforeunload', askConfirmation);


let slider = new Slider();
slider.init();

    //var collapsible = new Collapsible();
    //collapsible.init();
    
    $('.js-grid-enable').on('click', function(){
        $(this).toggleClass('active');
        $('body, body > header.header').toggleClass('baseline-16');
    });

    $('.js-need-confirmation').on('click', function(event){
        return confirm("This action is irreversible. Do you to want proceed ?");
    });
    $('.js-menu').on('click', function(){
        $('.site-panel').css('left', 0);
        $('.js-menu-close').show();
        $(this).hide();

    });
    $('.js-menu-close').on('click', function(){
        var panel = $('.site-panel');
        var left = '-' + panel.css('width');
        panel.css('left', left );
        $('.js-menu').show();
        $(this).hide();
    });
    /*
    $('form').on('change', function(event){
        prevent_leaving();
    });
    $('form .js-cancel').on('click', can_leave);
    */

    /*
    $('.mat-list').on('click', '.mat-list-item', function(){
        $(this).toggleClass('active');
    });
    */
    $('.js-dialog-open').on('click', function(){
        var target = $($(this).data('target'));
        target.show();
    });

    
    $('.js-dialog-close').on('click', function(){
        var target = $($(this).data('target'));
        target.hide();
        //var parent = $(this).parents('.dialog').hide();
        $('input[type!="hidden"]', target).val('');
    });
    $('.js-clear-input').on('click', function(){
        var target = $(this).data('target');
        $(':input', target).val('');
    });
    $('.js-reveal-btn').on('click', function(){
        var target = $(this).data('target');
        $('.js-revealable', target).show();
    });
    $('.js-revealable-hide').on('click', function(){
        console.log('hidding revealable inputs');
        var target = $(this).data('target');
        $('.js-revealable', target).hide();
    });
    
});


