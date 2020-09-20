/**
 * 
 * @param {*} options is a JSON defining the following data :
 * type - string
 * url - string
 * data - json
 * dataType - string
 * Example : 
 * type: 'POST',
   url : '/cart/add_to_cart/',
   data: {product_id: 102, quantity: 4},
   dataType: 'json'

   A future object is returned
 */
function ajax(options){
    return new Promise(function(resolve, reject){
        $.ajax(options).done(resolve).fail(reject);
    });
}



var Tabs = (function(){
    function Tabs(){
        this.currentTab     = 0;
        this.tabCount       = 0;
        this.tabs           = {};
        this.tab            = {};
        this.tabsCount      = 0;
        
    };

    Tabs.prototype.init = function(){
        this.tabsCount = $(".tabs").length;
        this.tabs = $(".tab-content");
        this.tab = $(".tab");
        this.tabCount = this.tab.length;
        if(this.tabCount == 0){
            return;
        }
        
        $('div.tab-container').each(function(){
            console.log("tab-container init...");
            $(this).find('div.tab-content:eq(0)').nextAll().hide();
        });
        //this.tabs.hide();
        $('div.tab-bar .tab').click(function(){
            var current = $(this);
            console.log("Tab clicked");
            console.log("current data : ", current.data('toggle'));
            
            if(!current.hasClass('active')){
                console.log("Has no class active");
                current.addClass('active').siblings().removeClass('active');
                $(current.data('toggle')).show().siblings('div.tab-content').hide();
            }
        });
    };
    Tabs.prototype.onTabClicked = function(event){
        var tab = parseInt($(event.target).data("index"));
        if(tab != this.currentTab){
            console.log("Tabs Plugin : Tab Clicked");
            this.currentTab = tab;
                this.update();
        }
    };
    Tabs.prototype.update = function(){
        this.tab.removeClass("active");
        $(this.tab[this.currentTab]).addClass("active");
        var that = this;
        this.tabs.hide();
        $(this.tabs[this.currentTab]).show();
    };
    return Tabs;
})();



var Slider = (function(){
    function Slider(){
        images_src = ['customer.png', 'businessman.png'];
    };

    Slider.prototype.init = function(){
       var slider =  $('#slider');
       var slides= slider.find('.slide');
       if(slides.length == 0){
           console.log("No slide found in this page");
           return;
       }

       console.log("slide found in this page : ", slides.length);
       slides.nextAll().hide();
       slides.first().html("I'm Slide 1");
    };

    return Slider;
})();


var Modal = (function(){
    function Modal(options){
        this.modal = {};
        this.init();
    }


    Modal.prototype.init = function(){
        that = this;
        var modals = $(".js-open-modal").click(function(event){
            var modal = $("#" + $(this).data('target'));
            that.modal = modal;
            modal.show();
            if(window){
                $(window).click(function(eventModal){
                    if(eventModal.target == modal.get(0)){
                        modal.hide();
                        that.modal = undefined;
                        var inputs = $('input.input-filter', modal);
                        inputs.val("");
                        $(inputs.data('update')).text("");
                    }
                });
            }
        });

        var modals = $(".js-close-modal").click(function(event){
            var target = $("#" + $(event.target).data('target'));
            that.modal = undefined;
            //console.log("opening modal ...");
            target.hide();
            var inputs = $('input.input-filter', target);
            inputs.val("");
            $(inputs.data('update')).text("");
        });

        

        console.log("Modal initialized");
    }

    Modal.prototype.create = function(options){
        var template = this.factories[options.factory].create();
        var modal = $(options.modal);
        $(".modal-content .modal-body", modal).append(template);
        //console.log("added into the modal");

    }
    return Modal;
})();



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



var Collapsible = (function(){
    function Collapsible(){
        this.$collapsible   = {}; // all element with collapsible class
        this.$close         = {}; // all button used to close a collapsible elements.

    }
    Collapsible.prototype.init = function(){
        console.log("Initializing Collapsible ...");
        this.$collapsible = $(".collapsible");
        //this.$close = this.$collapsible.find(".close");
        
        if(this.$collapsible.length == 0){
            console.log("No collapsible found on this page.");
            return;
        }
        this.$collapsible.children('.collapse-content').hide()
        console.log("Found " + this.$collapsible.length + " collapsibles on this pages.");
        $(this.$collapsible).on("click", ".open", function(event){
            console.log(this);
            var target =$(event.target).data("target");
            //var taret = $(this).siblings(".collapse-content");
            if(target == undefined){
                console.log("collpasible : target undefined");
                $(this).parent().children(".collapse-content").toggle();
            }
            else{
                $(target).toggle();
            }
        });

        $(this.$collapsible).on("click", ".close", function(event){
            event.stopPropagation();
            var target =$(event.target).data("target");

            if(target == undefined){
                $(this).parent().toggle();
            }
            else{
                $(target).toggle();
            }
        });

        console.log("Initializing Collapsible done.");
    };

    return Collapsible;
})();



var TableFilter = (function(){
    function TableFilter (){
        this.tables = {};
        this.rowStep = 5; // default number of row to display per page
        this.currentRowIndex = 0;
        this.numberOfRows = 0;
        this.rows = [];
        this.interval_start = {};
        this.interval_end = {};
        this.element_table_row_number = {};

    }
    TableFilter.prototype.init = function (){
       var that = this;
       this.tables = $(".js-filter-table");
       this.table = $('#employee-list');
       this.tableTbody = $('tbody', this.table);
       this.tr = $('tr', this.tableTbody).hide();
       this.numberOfRows = this.tr.length;
       this.element_table_row_number = $(".js-table-rows-number");
       this.interval_start = $(".js-table-interval-start");
       this.interval_end = $(".js-table-interval-end");
       var n = this.tables.length;
       var $select = $("#table-step");
       
       if(n == 0){
           console.log("No filter table found on this page");
           return;
       }
       Array.prototype.push.apply(this.rows, this.tr.toArray());
       if($select.length > 0){
            this.rowStep = $select.val();
            $select.on('change', function(event){
                that.setStep($select.val());
                console.log("table step changed to %s", that.rowStep );
            });
       }
       
       this.updateTable();
     
       console.log("%s filter table found on this page", n);

    }

    TableFilter.prototype.setStep = function(step){
        if(isNaN(step)){
            console.warn("TableFilter::setStep() : step is undefined");
            return;
        }
        var n = parseInt(step);
        if(n != this.rowStep){
            this.rowStep = n;
            this.updateTable();
        }
        
    }

    TableFilter.prototype.showRows = function(start, last){
        console.log("Table current rows interval :  start  - last  -> [%s - %s]", start, last);
            this.rows.forEach(function(tr, index){
                if(index >= start && index < last){
                    $(tr).show();
                }else{
                    $(tr).hide();
                }
            });
            this.interval_start.html(parseInt(start+1));
            this.interval_end.html(parseInt(last));
            this.element_table_row_number.html(parseInt(this.numberOfRows));
    }

    TableFilter.prototype.previous = function(){
        var start = 0;
        var last = 0;
        var tmp = this.currentRowIndex - this.rowStep;
        if( (this.currentRowIndex != 0) && !(tmp < 0)){
            last = this.currentRowIndex;
            start = tmp;
            this.currentRowIndex = start;
            this.showRows(start, last);
        }
    }
    
    TableFilter.prototype.next = function(){
        var start = 0;
        var last = 0;
        var tmp = this.currentRowIndex + this.rowStep;
        if(tmp < this.numberOfRows){
            start = tmp;
            this.currentRowIndex = start;
        }else{
            return;
        }
        if(start + this.rowStep < this.numberOfRows){
            last = start + this.rowStep;
        }else{
            last = this.numberOfRows;
        }
        this.showRows(start, last);
    }

    TableFilter.prototype.updateTable = function(){
        console.log("Table update entry :  currentIndex  - numberOfRows  -> [%s - %s]", this.currentRowIndex, this.numberOfRows);
        var start = this.currentRowIndex;
        var last = 0;
        var tmp = this.currentRowIndex + this.rowStep;
        if(tmp < this.numberOfRows){
            last = tmp;
        }else{
            last = this.numberOfRows;
        }
        this.showRows(start, last);
    }

    TableFilter.prototype.onAdd = function(event, n){
        if(isNaN(n)){
            console.warn("n is undefined");
            return;
        }
        var last = parseInt(n);
        for(var i = 0; i < last; i++){
            this.addRow({company: "novomind AG", name:"Cyrille Ngassam Nkwenga"});
        }
        this.updateTable();
        
    }
    TableFilter.prototype.addRow = function(data){
        var table = $('#employee-list');
        if(table.length == 0){
            console.log("No Employee List Table found");
            return;
        }
        if(typeof data == "undefined"){
            console.log("Data Table Error : data is undefined");
            return;
        }
        var attrs = ["company", "name"];
        var valid = attrs.every(function(e){
            return data.hasOwnProperty(e);
        });
        if(!valid){
            console.log("TableFilter.addRow : data is invalid");
            return;
        }
        this.numberOfRows++;
        var markup = `<tr><td class="checkbox"><input type="checkbox" name="selected"></td> <td>${data.company} - ${this.numberOfRows}</td> <td>${data.name}</td> </tr>`;
        var tbody = $('tbody', table);
        var $tr = $(markup).hide().appendTo(tbody);
        this.rows.push($tr);
    }

    TableFilter.prototype.fetchData = function(){
        console.log("TableFilter::fetchData () not implemented yet");
    }
    return TableFilter;
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

    var collapsible = new Collapsible();
    collapsible.init();
    
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

    $('.mat-list').on('click', '.mat-list-item', function(){
        $(this).toggleClass('active');
    });

    $('.js-dialog-open').on('click', function(){
        var target = $($(this).data('target'));
        target.show();
    });

    $("#amount-filter-input").on('keyup', function(event){
        var input = $(this);
        $(input.data('update')).text(input.val());
    });

    $('.js-list-filter').on('click', function(){
        var inputs_container = $('#inputs');
        var el = $(this);
        var input = $('<input/>', {
            id: el.data('name') + "-" + el.data('value'),
            type: 'text',
            name : el.data('name'),
            value: el.data('value'),
        });
        el.addClass('selected');
        inputs_container.append(input);
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


