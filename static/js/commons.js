

var ListFilter = (function(){
    function ListFilter(){
        console.log("creating ListFilter instance");
        this.init();
        console.log("ListFilter instance created");
    };

    ListFilter.prototype.init = function(){
        console.log("ListFilter instance initializing");
        $('.js-list-filter').on('keyup', function(event){
            event.stopPropagation();
            var value = this.value.trim().toLowerCase();
            var target_container = this.getAttribute('data-target');
            var el = this.getAttribute('data-element');
            $('#' + target_container + " " +  el).filter(function(){
                $(this).toggle(this.getAttribute('data-value').toLowerCase().includes(value));
            });
        });

        console.log("ListFilter instance initialized");
    };


    return ListFilter;
})();


$(document).ready(function(){
    var listfilter = new ListFilter();
    $('.collapsible .toggle').on('click', function(event){
        var parent = $(this).parent();
        var target = $('.' + this.getAttribute('data-toggle'), parent);
        $('input', parent).val('');
        target.toggle();
    });
});