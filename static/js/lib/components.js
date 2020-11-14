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
            $(this).find('div.tab-content:eq(0)').nextAll().hide();
        });
        //this.tabs.hide();
        $('div.tab-bar .tab').click(function(){
            var current = $(this);
            
            if(!current.hasClass('active')){
                current.addClass('active').siblings().removeClass('active');
                $(current.data('toggle')).show().siblings('div.tab-content').hide();
            }
        });
    };
    Tabs.prototype.onTabClicked = function(event){
        var tab = parseInt($(event.target).data("index"));
        if(tab != this.currentTab){
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
           return;
       }
       slides.nextAll().hide();
       slides.first().html("I'm Slide 1");
    };

    return Slider;
})();

var Collapsible = (function(){
    function Collapsible(){
        this.$collapsible   = {}; // all element with collapsible class
        this.$close         = {}; // all button used to close a collapsible elements.

    }
    Collapsible.prototype.init = function(){
        this.$collapsible = $(".collapsible");
        
        if(this.$collapsible.length == 0){
            return;
        }
        //this.$collapsible.children('.collapse-content').hide()
        $('.collapsible').on('click', '.collapse-toggle', function(){
            $('#' + $(this).data('target')).toggle();
        });
        $(this.$collapsible).on("click", ".open", function(event){
            var target =$(event.target).data("target");
            if(target == undefined){
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
    };

    return Collapsible;
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
            target.hide();
            var inputs = $('input.input-filter', target);
            inputs.val("");
            $(inputs.data('update')).text("");
        });
    }

    Modal.prototype.create = function(options){
        var template = this.factories[options.factory].create();
        var modal = $(options.modal);
        $(".modal-content .modal-body", modal).append(template);

    }
    return Modal;
})();
