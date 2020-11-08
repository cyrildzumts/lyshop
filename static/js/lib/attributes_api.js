define(function() {
    'use strict';
    console.log("attribute_api creation ...");
    function AttributManager(){
        
        //this.form = $('#form-attrs-management');
        this.form =$('#form-add-attributes');
        this.form_attributes = $('#form-add-attributes');
        this.form_attr_container = $('#form-attr-container', this.form);
        this.attrs_container = $('#form-attr-container', this.form);
        this.attrs_inputs = [];
        this.total_form = 0;
        this.input_max_length = 32;
        this.replace_pattern = /\d+/g;
        this.id_form_TOTAL_FORMS = $("#id_form-TOTAL_FORMS", this.form);
        this.id_form_INITIAL_FORMS = $("#id_form-INITIAL_FORMS", this.form);
        this.id_form_MIN_NUM_FORMS = $("#id_form-MIN_NUM_FORMS", this.form);
        this.id_form_MAX_NUM_FORMS = $("#id_form-MAX_MIN_FORMS", this.form);
        console.log("AttributeManager created ...");
    };
    AttributManager.prototype.init = function(){
        var self = this;
        $('.js-add-new-attribute').on('click', function(){
            //var target = $($(this).data('target'));
            //var form_container = $($(this).data('form'));
            self.create_attribute();
        });
        console.log("AttributeManager initialized ...");
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
        delete_button.append($("<i/>", {
            'class': 'fas fa-backspace icon'
        }));
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
            'maxlength': self.input_max_length
        });
        input_name.appendTo(label_name);
        var label_display_name = $("<label/>").text(attr_template.display_name + " : ");
        var input_display_name = $('<input type="text">').attr({
            'id':`id-form-${this.total_form}-display_name`,
            'name': `form-${this.total_form}-display_name`,
            'maxlength': self.input_max_length
        });
        input_display_name.appendTo(label_display_name);
        var label_value = $("<label/>").text(attr_template.value + " : ");
        var input_value = $('<input type="text">').attr({
            'id':`id-form-${this.total_form}-value`,
            'name': `form-${this.total_form}-value`,
            'maxlength': self.input_max_length
        });
        input_value.appendTo(label_value);

        var label_primary = $("<label/>").text(attr_template.is_primary + " : ");
        var input_primary = $('<input type="checkbox">').attr({
            'id':`id-form-${this.total_form}-primary`,
            'name': `form-${this.total_form}-is_primary`
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
        div.appendTo(self.form_attr_container);
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
        var self = this;
        this.attrs_inputs.forEach(function (arr_input, index) {
            arr_input.forEach(function(e, i){
                self.updateInputIndex(e, index);
            });
        });
    };

    AttributManager.prototype.decremente_management_form = function(){
        this.total_form = this.total_form - 1;
        this.id_form_TOTAL_FORMS.val(this.total_form);
        this.id_form_MIN_NUM_FORMS.val(this.total_form);
        this.id_form_MAX_NUM_FORMS.val(this.total_form);
    };

    return AttributManager;
});
