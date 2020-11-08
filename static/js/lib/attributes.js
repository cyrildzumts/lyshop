var id_form_TOTAL_FORMS;
var id_form_INITIAL_FORMS;
var id_form_MIN_NUM_FORMS;
var id_form_MAX_NUM_FORMS;
var formset_prefix = 'form';
var total_form = 0;
var input_max_length = 32;
var attr_list = [];
var replace_pattern = /\d+/g;

function create_attribute(index){
    console.log("Adding attribute");
    var id = `attr-form-${index}`;
    var div = $('<div/>', {
        'class': 'row',
        'id': id
    });
    var delete_button = $("<button/>", {
        'id': id + '-delete-btn',
        'data' : {'target': '#' + id},
        'text': 'Delete',
        'class' : 'mat-button mat-button-default'
    });
    delete_button.on('click', function(){
        div.remove();
        decremente_management_form(form);
        console.log("Removed attribute with id \"%s\"", id);
    });
    var label_name = $("<label/>").text(attr_template.name + " : ");
    var input_name = $('<input type="text">').attr({
        'id':`id-form-${index}-name`,
        'name': `form-${index}-name`,
        'maxlength': input_max_length
    });
    input_name.appendTo(label_name);
    var label_display_name = $("<label/>").text(attr_template.display_name + " : ");
    var input_display_name = $('<input type="text">').attr({
        'id':`id-form-${index}-display_name`,
        'name': `form-${index}-display_name`,
        'maxlength': input_max_length
    });
    input_display_name.appendTo(label_display_name);
    var label_value = $("<label/>").text(attr_template.value + " : ");
    var input_value = $('<input type="text">').attr({
        'id':`id-form-${index}-value`,
        'name': `form-${index}-value`,
        'maxlength': input_max_length
    });
    input_value.appendTo(label_value);
    var label_primary = $("<label/>").text(attr_template.is_primary + " : ");
    var input_primary = $('<input type="checkbox">').attr({
        'id':`id-form-${index}-primary`,
        'name': `form-${index}-is_primary`
    });

    input_primary.appendTo(label_primary);
    var label_value_type = $("<label/>").text(attr_template.value_type + " : ");
    var select_value_type = $('<select/>').attr({
        'id':`id-form-${index}-value_type`,
        'name': `form-${index}-value_type`,
    });
    select_value_type.appendTo(label_value_type);
    $('<option/>', {
        'selected': 'selected',
        'value': undefined,
        'text' : "Select a type"
    }).appendTo(select_value_type);
    attr_template.value_types.forEach(function(el, index){
        $('<option/>', {
            'value': el.key,
            'text' : el.value
        }).appendTo(select_value_type);
    });
    var input_form_id = $('<input type="hidden">').attr({
        'id':`id-form-${index}-id`,
        'name': `form-${index}-id`,
    });
    div.append([label_name, label_display_name, label_value, label_value_type,label_primary ,input_form_id, delete_button]);
    div.appendTo(container);
    incremente_management_form(form);
    console.log("[OK] Adding attribute done!");
    return div;
}

var AttributManager = (function(){
    function AttributManager(options){
        this.form = $('#form-attrs-management');
        this.attrs_container = $('#attrs-container', this.form);
        this.attrs_inputs = [];
        this.total_form = 0;
        this.replace_pattern = replace_pattern;
        this.id_form_TOTAL_FORMS = $("#id_form-TOTAL_FORMS", this.form);
        this.id_form_INITIAL_FORMS = $("#id_form-INITIAL_FORMS", this.form);
        this.id_form_MIN_NUM_FORMS = $("#id_form-MIN_NUM_FORMS", this.form);
        this.id_form_MAX_NUM_FORMS = $("#id_form-MAX_MIN_FORMS", this.form);
    };
    AttributManager.prototype.init = function(){

    };

    AttributManager.prototype.addAttribute = function(){

    };

    AttributManager.prototype.removeAttribute = function(){

    };

    AttributManager.prototype.clear = function(){
        this.total_form = 0;
        this.updateManagementForm();

    };

    AttributManager.prototype.updateFormInputIndex = function(){
        var name;
        var id;
        var self = this;
        this.attrs_inputs.forEach(function (arr_input, index) {
            arr_input.forEach(function(e, i){
                self.updateInputIndex(e, index);
            });
        });
    };

    AttributManager.prototype.updateInputIndex = function(input, index){
        var name = input.attr('name');
        var id = input.attr('id');
        input.attr({
            id: id.replace(this.replace_pattern, index),
            name: name.replace(this.replace_pattern, index)
        });
    }

    AttributManager.prototype.create_attribute = function(){
        console.log("Adding attribute");
        var self = this;
        var id = `attr-form-${this.total_form}`;
        var div = $('<div/>', {
            'class': 'row',
            'id': id
        });
        var delete_button = $("<button/>", {
            'id': id + '-delete-btn',
            'text': 'Delete',
            'class' : 'mat-button mat-button-default'
        }).attr({
            'data-target': '#' + id
        });
        delete_button.on('click', function(){
            div.remove();
            self.decremente_management_form();
            self.updateFormInputIndex();
            console.log("Removed attribute with id \"%s\"", id);
        });
        var label_name = $("<label/>").text(attr_template.name + " : ");
        var input_name = $('<input type="text">').attr({
            'id':`id-form-${this.total_form}-name`,
            'name': `form-${this.total_form}-name`,
            'maxlength': input_max_length
        });
        input_name.appendTo(label_name);
        var label_display_name = $("<label/>").text(attr_template.display_name + " : ");
        var input_display_name = $('<input type="text">').attr({
            'id':`id-form-${this.total_form}-display_name`,
            'name': `form-${this.total_form}-display_name`,
            'maxlength': input_max_length
        });
        input_display_name.appendTo(label_display_name);
        var label_value = $("<label/>").text(attr_template.key + " : ");
        var input_value = $('<input type="text">').attr({
            'id':`id-form-${this.total_form}-value`,
            'name': `form-${this.total_form}-value`,
            'maxlength': input_max_length
        });
        input_value.appendTo(label_value);

        var label_primary = $("<label/>").text(attr_template.is_primary + " : ");
        var input_primary = $('<input type="checkbox">').attr({
            'id':`id-form-${index}-primary`,
            'name': `form-${index}-is_primary`
        });
        input_primary.appendTo(label_primary);
        var label_value_type = $("<label/>").text(attr_template.value_type + " : ");
        var select_value_type = $('<select/>').attr({
            'id':`id-form-${this.total_form}-value_type`,
            'name': `form-${this.total_form}-value_type`,
        });
        select_value_type.appendTo(label_value_type);
        $('<option/>', {
            'selected': 'selected',
            'value': undefined,
            'text' : "Select a type"
        }).appendTo(select_value_type);
        attr_template.value_types.forEach(function(el, index){
            $('<option/>', {
                'value': el.key,
                'text' : el.value
            }).appendTo(select_value_type);
        });
        var input_form_id = $('<input type="hidden">').attr({
            'id':`id-form-${this.total_form}-id`,
            'name': `form-${this.total_form}-id`,
        });
        div.append([label_name, label_display_name, label_value, label_value_type, label_primary, input_form_id, delete_button]);
        div.appendTo(container);
        self.incremente_management_form();
        self.attrs_inputs.push([input_name, input_display_name, input_value, select_value_type, input_primary, input_form_id]);
        console.log("[OK] Adding attribute done!");
        return div;
    };

    AttributManager.prototype.incremente_management_form = function(){
        this.total_form = this.total_form + 1;
        this.id_form_TOTAL_FORMS.val(this.total_form);
        this.id_form_MIN_NUM_FORMS.val(this.total_form);
        this.id_form_MAX_NUM_FORMS.val(this.total_form);
    };

    AttributManager.prototype.updateManagementForm = function(){
        this.id_form_TOTAL_FORMS.val(this.total_form);
        this.id_form_MIN_NUM_FORMS.val(this.total_form);
        this.id_form_MAX_NUM_FORMS.val(this.total_form);
    };

    AttributManager.prototype.decremente_management_form = function(){
        this.total_form = this.total_form - 1;
        this.id_form_TOTAL_FORMS.val(this.total_form);
        this.id_form_MIN_NUM_FORMS.val(this.total_form);
        this.id_form_MAX_NUM_FORMS.val(this.total_form);
    };



    return AttributManager;
})();

function updateInputIndex(input, index){
    var name = input.attr('name');
    var id = input.attr('id');
    var new_name = name.replace(replace_pattern, index);
    var new_id = id.replace(replace_pattern, index);
    console.log("Updating input with id \"%s\" - name = \"%s\" with index \"%s\"", id, name, index);
    input.attr({
        id: new_id,
        name: new_name
    });
    console.log("Updated input with id \"%s\" - name = \"%s\" with index \"%s\"", new_id, new_name, index);
}

function incremente_management_form(container){
    total_form = total_form + 1;
    $("#id_form-TOTAL_FORMS", container).val(total_form);
    $("#id_form-MAX_NUM_FORMS", container).val(total_form);
    $("#id_form-MIN_NUM_FORMS", container).val(total_form);
}

function decremente_management_form(container){
    total_form = total_form - 1;
    $("#id_form-TOTAL_FORMS", container).val(total_form);
    $("#id_form-MAX_NUM_FORMS", container).val(total_form);
    $("#id_form-MIN_NUM_FORMS", container).val(total_form);
}

function updateManagementForm(){
    var name;
        var id;
        attr_list.forEach(function (arr_input, index) {
            arr_input.forEach(function(e, i){
                updateInputIndex(e, index);
            });
        });
}

function create_attribute_entry(container, form){
    console.log("Adding attribute");

    var id = `attr-form-${total_form}`;
    var div = $('<div/>', {
        'class': 'row',
        'id': id
    });
    var delete_button = $("<button/>", {
        'id': id + '-delete-btn',
        'text': 'Delete',
        'class' : 'mat-button mat-button-default'
    }).attr({
        'data-target': '#' + id,
        'data-index': total_form
    });
    delete_button.on('click', function(){
        var attr_index = $(this).data('index');
        var attr = attr_list[attr_index];
        attr_list.splice(attr_index, 1);
        div.remove();
        decremente_management_form(form);
        updateManagementForm();
        console.log("Removed attribute with id \"%s\"", id);
    });
    var label_name = $("<label/>").text(attr_template.name + " : ");
    var input_name = $('<input type="text">').attr({
        'id':`id-form-${total_form}-name`,
        'name': `form-${total_form}-name`,
        'maxlength': input_max_length
    });
    input_name.appendTo(label_name);
    var label_display_name = $("<label/>").text(attr_template.display_name + " : ");
    var input_display_name = $('<input type="text">').attr({
        'id':`id-form-${total_form}-display_name`,
        'name': `form-${total_form}-display_name`,
        'maxlength': input_max_length
    });
    input_display_name.appendTo(label_display_name);
    var label_value = $("<label/>").text(attr_template.value + " : ");
    var input_value = $('<input type="text">').attr({
        'id':`id-form-${total_form}-value`,
        'name': `form-${total_form}-value`,
        'maxlength': input_max_length
    });
    input_value.appendTo(label_value);
    var label_value_type = $("<label/>").text(attr_template.value_type + " : ");
    var select_value_type = $('<select/>').attr({
        'id':`id-form-${total_form}-value_type`,
        'name': `form-${total_form}-value_type`,
    });
    select_value_type.appendTo(label_value_type);
    $('<option/>', {
        'selected': 'selected',
        'value': undefined,
        'text' : "Select a type"
    }).appendTo(select_value_type);
    attr_template.value_types.forEach(function(el, index){
        $('<option/>', {
            'value': el.key,
            'text' : el.value
        }).appendTo(select_value_type);
    });
    var label_primary = $("<label/>").text(attr_template.is_primary + " : ");
    var input_primary = $('<input type="checkbox">').attr({
        'id':`id-form-${total_form}-value`,
        'name': `form-${total_form}-is_primary`,
        'maxlength': input_max_length
    });
    input_primary.appendTo(label_primary);
    var input_form_id = $('<input type="hidden">').attr({
        'id':`id-form-${total_form}-id`,
        'name': `form-${total_form}-id`,
    });
    div.append([label_name, label_display_name, label_value, label_value_type, label_primary, input_form_id, delete_button]);
    attr_list.push([input_name, input_display_name, input_value, select_value_type, input_primary, input_form_id]);
    div.appendTo(container);
    incremente_management_form(form);
    console.log("[OK] Adding attribute done!");
    return div;
}


$(document).ready(function(){

    $('.js-add-new-attribute').on('click', function(){
        var target = $($(this).data('target'));
        var form_container = $($(this).data('form'));
        create_attribute_entry(target, form_container);
    });
    /*
    $('.variant-attr-input').on('change', function(){
        var target = '#' + $(this).data('target');
        var len = $('variant-attr-input').filter(function(){
            return this.checked;
        }).length;
        $(target).toggle('hidden', len == 0)
    });
    */
});