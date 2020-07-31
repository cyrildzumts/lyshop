

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

    ListFilter.prototype.filter = function(ctx, filter_field, value_list){
        if(!ctx || !filter_field || !value_list || value_list.length == 0){
            console.log("Filter called with missing argumtent");
            return;
        }
        console.log("Filtering started");
        $(".filterable", ctx).each(function(index, element){
            let filter_value = this.getAttribute(filter_field);
            console.log(" Filter Field = \"%s\" - Filter Value = \"%s\" - Value List = [\"%s\"]", filter_field ,filter_value, value_list)
            $(this).toggle(value_list.includes(filter_value));
        });
        console.log("Listfilter : filter run with success");
    };

    ListFilter.prototype.reset_filter = function(ctx, container){
        if(!ctx || !container){
            console.log(" Reset Filter called with missing context");
            return;
        }
        $("input:checkbox", ctx).each(function(){
            this.checked = false;
        });
        $(".filterable", container).each(function(index, element){
            $(this).show();
        });
        console.log("Listfilter : reset run with success");
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

    $('.js-filter-btn').on('click', function(event){
        var ctx = $('#' + this.getAttribute('data-context'));
        var input_name = this.getAttribute('data-input-name');
        var container = this.getAttribute('data-container');
        var filter_field = this.getAttribute("data-filter-field");
        var value_list = [];
        $("input:checked[name=\"" + input_name + "\"]", ctx).each(function(){
            console.log("adding value to filter : %s", this.getAttribute("data-value"));
            value_list.push(this.getAttribute("data-value"));
        });
        listfilter.filter(container, filter_field, value_list);
    });

    $('.js-filter-reset-btn').on('click', function(event){
        var ctx = $('#' + this.getAttribute('data-context'));
        var container = this.getAttribute('data-container');
        listfilter.reset_filter(ctx, container);
    });
});