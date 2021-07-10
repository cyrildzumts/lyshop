define(function() {
    'use strict';

var Tabs = (function(){
    var tab_preffix = "step-header-";
    var tab_content_prefix = "step-";
    var checked_icon_class = "fas fa-check";
    var tab_title_class = "tab-title";
    var tab_title_checked = "tab-checked";
    var tab_contents = $('.tab-content');
    var tab_list = $('.tab');
    var current_index = 0;
    var tab_content_validators = [];
    var valid_tabs = [];
    var tabs_to_skips = [];

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
        var that = this;
        
        $('div.tab-container').each(function(){
            $(this).find('.tab-content:eq(0)').nextAll().hide();
        });
        //this.tabs.hide();
        $('div.tab-bar .tab').click(function(){
            var current = $(this);
            
            if(!current.hasClass('active')){
                current.addClass('active').siblings().removeClass('active');
                $(current.data('toggle')).show().siblings('div.tab-content').hide();
            }
        });
        $('.js-tab').on('click', function(){
            var tab_content = $($(this).data('toggle'));
            var tab_index = parseInt(tab_content.data('index'));
            $('.tab').eq(tab_index).addClass('active').siblings().removeClass('active');
            tab_content.show().siblings('.tab-content').hide();
        });
        console.log("Tabs initialised");
    };

    Tabs.prototype.add_validator = function(validator, index){
        if("function" == typeof validator){
            tab_content_validators[index] = validator;
        }else{
            console.warn("validator must be a callable object");
        }
        
    };

    Tabs.prototype.toggle_checked = function(index, toggle){
        if(index < 0 || index > this.tabCount){
            console.warn("No tab with index %s", index);
            return;
        }
        $('.' + tab_preffix + index + " .icon").toggleClass(checked_icon_class, toggle);
        $('.' + tab_preffix + index + " ." + tab_title_class).toggleClass(tab_title_checked, toggle);
        $('#' + tab_content_prefix + index + " .js-tab-next").toggleClass('disabled', !toggle);
        $('.js-send').prop('disabled', !toggle).toggleClass('disabled', !toggle);
        var index_included = valid_tabs.includes(index);
        if(toggle && !index_included ){
            valid_tabs.push(index);
        }else if(!toggle && index_included){
            valid_tabs.splice(index, 1);
        }

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

var Carousel = (function(){
    function Carousel(){
        this.carousel = document.querySelector('.carousel');
        this.items = document.querySelector('.carousel-items');
        this.dots = document.querySelector('.dot');
        this.next = document.querySelector('.carousel-control.next');
        this.prev = document.querySelector('.carousel-control.prev');
        this.total = this.items.length -1;
        this.active = 'active';
        this.current = 0;

    }

    Carousel.prototype.init = function(){
        if(this.carousel.length == 0)return;
        this.prev.addEventListener('click', this.scrollPrev.bind(this));
        this.next.addEventListener('click', this.scrollNext.bind(this));
        console.log("Carousel initialized");
    }

    Carousel.prototype.setActivedot = function(){
        var self = this;
        this.dots.forEach(dot, i => {
            i == self.current ? dot.classList.add(self.active): dot.classList.remove(self.active)
        });
    }

    Carousel.prototype.scrollToCurrent = function(){
        var self = this;
        this.items.getElementsByClassName.transform = `translateX(${current * -100}%)`;
        this.setActivedot();
    }

    Carousel.prototype.scrollPrev = function(){
        if(this.current === 0) return;
        this.current--;
        this.scrollToCurrent();
    }

    Carousel.prototype.scrollNext = function(){
        if(this.current === this.total) return;
        this.current++;
        this.scrollToCurrent();
    }

    return Carousel;
})();

var Collapsible = (function(){
    function Collapsible(){
        this.$collapsible   = {}; // all element with collapsible class
        this.$close         = {}; // all button used to close a collapsible elements.

    }
    Collapsible.prototype.init = function(){
        this.$collapsible = $(".collapsible");
        var filter_content = $('#filter-content');
        if(this.$collapsible.length == 0){
            return;
        }
        $('.collapsible').on('click', '.collapse-toggle', function(event){
            event.stopPropagation();
            var content  = $('#' + $(this).data('target'));
            if(content.eq(filter_content)|| content.parent().eq(filter_content)){
                $('.collapsible .collapse-content', filter_content).not(content).hide();
            }else{
                $('.collapsible .collapse-content').not(content).hide();
            }
            content.toggle();
            //$('input.clearable', content).val('');
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
        var that = this;
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
var Component = {
    modal : new Modal(),
    collapsible : new Collapsible(),
    tabs : new Tabs(),
    carousel : new Carousel(),
    initComponent : function(){
        this.modal.init();
        this.tabs.init();
        this.collapsible.init();
        this.carousel.init();
        console.log("Component module initialized");
    }
};
return Component;

});
