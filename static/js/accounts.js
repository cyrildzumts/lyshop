function account_form_validation(){
    console.log("Account form validation not implemented yet.")
    return true;
}


function activate_editable_inputs(context){
    console.debug("activating editableinputs");
    var $editable_inputs = $('input.js-editable', context);
    $editable_inputs.addClass('editable');
}

function deactivate_editable_inputs(context){
    console.debug("deactivating editableinputs");
    var $editable_inputs = $('input.js-editable', context);
    $editable_inputs.removeClass('editable');
}


function init(){
    var $editable_inputs = $('input.js-editable');
    $editable_inputs.removeClass('editable');
}

$(document).ready(function(){
    init();
    $('.js-edit-form').on('click', function(event){
        var ctx = $($(this).data('target'));
        activate_editable_inputs(ctx);
    });

    $('.js-form-edit-cancel').on('click', function(event){
        var ctx = $($(this).data('target'));
        deactivate_editable_inputs(ctx);
    });
});