$('.js-custom-input').on('click', function(event){
    $(this).toggle();
    $('input', this).toggle();
});

$('.js-custom-input .js-edit').on('click', function(event){
    $(this).parent().toggle();
    $(this).sibblings('input').toggle();
});

$('.js-custom-input input').on('keyup change', function(event){
    var $el = $(this);
    $el.parent().html($el.val());
});

$('.js-custom-input .js-edit-close').on('click', function(event){
    var $el = $(this).sibblings('input');
    $el.parent().html($el.val());
    $(this).parent().toggle();
    $(this).hide();
    $el.hide();
});

