var fileUpload;


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

var DragDrop = (function(){

    function DragDrop(){

    };

    DragDrop.prototype.init = function(){

    };

    DragDrop.prototype.accept = function(event){

    };

    DragDrop.prototype.drag = function (event) {
        
    };

    return DragDrop;
})();

function onDropHandler(event){
    console.log("File(s) dropped");
    event.preventDefault();
    var files = [];
    if(event.dataTransfer.items){
        var items = event.dataTransfer.items;
        for(var i = 0; i < items.length; i++){
            if(items[i].kind === 'file'){
                var file = items[i].getAsFile();
                fileUpload.addFile(file);
                console.log("...asFile file[" + i + "].name = " + file.name);
            }
        }
    }else{
        var files = event.dataTransfer.files;
        //fileUpload.setFiles(files);
        for(var i = 0; i < files.length; i++){
            //var file = files[i]
            fileUpload.addFile(files[i]);
            console.log("... file[" + i + "].name = " + files[i].name);
        }
    }
    $('.drag-area').removeClass('on-drag');
}


function onDragOverHandler(event){
    console.log("File(s) in drop area");
    event.preventDefault();
    

}

function onDragStartHandler(event) {
    console.log("Drag start");
    $('.drag-area').addClass('on-drag');
    
}
function onDragEndHandler(event) {
    console.log("Drag end");
    $('.drag-area').removeClass('on-drag');
    
}

function uploadFiles(form, files) {
    console.log("SendForm started ...");
    var formData = new FormData(form);
    files.forEach(function(file, index){
        formData.append("file_" + index, file, file.name);
    });
    $(form).serializeArray().forEach(function(input, index){
        formData.append(input.name, input.value);
    });
    var options = {
        url : $(form).attr('action'),
        type: 'POST',
        enctype : 'multipart/form-data',
        data : formData,
        processData : false,
        cache : false,
        contentType : false
    };
    ajax(options).then(function(response){

    }, function(reason){

    });
    
}


var FileUpload = (function(){
    function FileUpload(){
        this.files = [];
        this.form = undefined;
        this.formData = undefined;
        this.clean = true;
        this.drag_area = $('.drag-area');
        this.file_list_container = $('.file-list');
        this.file_entries = {};
        this.empty_element = $('.no-data', this.file_list_container);
        this.send_btn = $('.js-send-file-upload-btn');
        this.clear_btn = $('.js-file-list-clear-btn');
        this.init();
    };

    FileUpload.prototype.init = function(){
        var that = this;
        this.clear_btn.on('click', this.clear.bind(this));
    };

    FileUpload.prototype.clear = function() {
        console.log("clear file list ...");
        console.log(this);
        this.files = [];
        this.formData = undefined;
        this.form = undefined;
        this.clean = true;
        //$('.file-entry', this.file_list_container).remove();
        this.file_list_container.empty().append(this.empty_element);
        this.drag_area.removeClass('non-empty');
        this.send_btn.addClass('disabled').prop('disabled',true);
        this.clear_btn.addClass('hidden');
        console.log("[OK] cleared file list");
    };

    FileUpload.prototype.isClean = function() {
        return this.clean;
    };

    FileUpload.prototype.setForm = function(form){
        this.form = form;
        this.clean = false;
        return this;
    };

    FileUpload.prototype.setFiles = function(files){
        this.files = files;
        this.clean = false;
        return this;
    };

    FileUpload.prototype.addFile = function(file){
        if(this.files.some(f => f.name == file.name)){
            console.warn("A file with the same name already exists.")
            return this;
        }
        var that = this;
        this.files.push(file);
        var li = $('<li />',{
            id:"file-" + that.files.length,
            'class' : 'file-entry',
            'title': file.name,
        });
        var entry_text = $('<span />', {
            text: file.name
        });
        var entry_remove_btn = $('<button />', {
            class: 'mat-button mat-button-text',
            type: 'button'
        }).append($('<i />', {
            class: 'fas fa-times icon'
        }));
        entry_remove_btn.on('click', function(event){
            event.preventDefault();
            event.stopPropagation();
            that.removeFile([file.name]);
            li.remove();
        });
        li.append(entry_text, entry_remove_btn).appendTo(that.file_list_container);
        $('.no-data', that.file_list_container).remove();
        this.drag_area.addClass('non-empty');
        this.send_btn.removeClass('disabled').prop('disabled',false);
        this.clear_btn.removeClass('hidden');
        this.clean = false;
        return this;
    };

    FileUpload.prototype.removeFile = function(fileNames){
        console.log("removing files : %s", fileNames);
        var old_length = this.files.length;
        this.files = this.files.filter(f => !fileNames.includes(f.name));
        if(this.files.length != old_length && this.files.length < old_length){
            console.log("removed files : %s", fileNames);
            if(this.files.length == 0){
                this.file_list_container.append(this.empty_element);
                this.drag_area.removeClass('non-empty');
                this.send_btn.addClass('disabled').prop('disabled',true);
                this.clear_btn.addClass('hidden');
            }
            this.clean = false;
        }else{
            console.log("files : %s not removed", fileNames);
            
        }
        
        return this;
    };
    FileUpload.prototype.update = function(){
        if(this.isClean()){
            console.warn("FileUpload can not be updated. formData is already clean.");
            return;
        }
        if(!this.form || !this.files || this.files.length == 0){
            console.warn("FileUpload can not be updated. form or files are missing.");
            return;
        }
        this.formData = new FormData(this.form);
        var that = this;
        this.files.forEach(function(file, index){
            that.formData.append("file_" + index, file, file.name);
        });
        this.clean = true;
        /*
        $(form).serializeArray().forEach(function(input, index){
            formData.append(input.name, input.value);
        });
        */
    };

    FileUpload.prototype.canSend = function(){
        let formValid = typeof this.form != 'undefined';
        let filesValid = typeof this.files != 'undefined';

        return formValid && filesValid && this.files.length > 0;
    };

    FileUpload.prototype.getForm = function() {
        return this.form;
    };

    FileUpload.prototype.getFiles = function() {
        return this.files;
    }

    FileUpload.prototype.getFormDate = function() {
        return this.formData;
    }

    FileUpload.prototype.upload = function(){
        if(!this.canSend()){
            console.error("Files can not be sent. Please check your files form. Files or form are missing.");
            return;
        }
        if(typeof ajax === 'undefined'){
            var errorMsg = "can not upload files. ajax funtion is not defined";
            console.error(errorMsg);
            throw new Error(errorMsg);
        }
        var that = this;
        var options = {
            url : $(this.form).attr('action'),
            type: 'POST',
            enctype : 'multipart/form-data',
            data : this.formData,
            processData : false,
            cache : false,
            contentType : false
        };
        ajax(options).then(function(response){
            console.info("Files have bean uploaded.");
            fileUpload.clear();

        }, function(reason){
            console.error("Files could not be uploaded.");
            console.error(reason);
            fileUpload.clear();
        });

    };

    return FileUpload;
})();

function kiosk_update(event){
    console.log("Kios update...");
    document.getElementById('main-image').src = event.target.src;
    $(".kiosk-image").removeClass('active').filter(event.target).addClass("active");
}

function dateFormat(input){
    console.log(input);
    console.log("Date Value : %s", input.value);
}

$(document).ready(function(){
    var listfilter = new ListFilter();
    fileUpload = new FileUpload();
    $('.collapsible .toggle').on('click', function(event){
        var parent = $(this).parent();
        var target = $('.' + this.getAttribute('data-toggle'), parent);
        $('input', parent).val('');
        target.toggle();
    });

    $('#shipment-form').on('submit',function(event){
        event.preventDefault();
        event.stopPropagation();
        $('input[type="date"]').each(i => dateFormat(i.value));
        return false;
    });

    $('.js-filter-btn').on('click', function(event){
        var ctx = $('#' + this.getAttribute('data-context'));
        var input_name = this.getAttribute('data-input-name');
        var container = $('#' + this.getAttribute('data-container'));
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
        var container = $('#' + this.getAttribute('data-container'));
        listfilter.reset_filter(ctx, container);
    });

    $('#file-upload-form').on('submit', function(event){
        console.log("submitting file-upload-form");
        event.preventDefault();
        event.stopPropagation();
        console.log(this);
        fileUpload.setForm(this);
        fileUpload.update();
        fileUpload.upload();
        //return false;
        
    });
    $('.js-select-image').on('click', kiosk_update);
    $('.js-select-image').first().click();
});