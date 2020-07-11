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

function add_to_cart(product){
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-add-to-cart/',
        data : {product:product.id, quantity:product.quantity, csrfmiddlewaretoken: csrfmiddlewaretoken.val()}
    }
    console.log('Adding product %s into user cart', product.name);
    add_promise = ajax(option).then(function(response){
        console.log("Product %s added into cart", product.name);
        console.log(response);
        //$("#cart-badge").text(response.count)
        document.getElementById('cart-badge').textContent = response.count;
    }, function(reason){
        console.error("Error on adding Product %s into cart", product.name);
        console.error(reason);
    });
}

function add_to_coupon(){
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
    var coupon = $('#coupon').val();
    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-add-coupon/',
        data : {coupon:coupon, csrfmiddlewaretoken: csrfmiddlewaretoken.val()}
    }
    add_promise = ajax(option).then(function(response){
        console.log(response);
        /*
        context['reduction'] 
        context['total']
        */
        document.getElementById('reduction').textContent = response.reduction;
        document.getElementById('total').textContent = response.total;
    }, function(reason){
        console.error("Error on adding Coupon \"%s\" to user cart", coupon);
        console.error(reason);
    });
}

function form_submit_add_cart(){
    var form = $('#add-cart-form');
    if(form.length < 0){
        console.log("No add to cart form found");
        return;
    }
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]', form);
    var data = {};
    var inputs = form.serializeArray();

    inputs.forEach(function(v,index){
        console.log("name : %s - value : %s", v.name, v.value)
        data[v.name] = v.value;
    });    
    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-add-to-cart/',
        data : data
    }
    console.log("inputs : %s", inputs.length);
    console.log("data : ", data);
    console.log("option : ", option);
    
    add_promise = ajax(option).then(function(response){
        console.log("Product added into cart");
        console.log(response);
        //$("#cart-badge").text(response.count)
        document.getElementById('cart-badge').textContent = response.count;
    }, function(reason){
        console.error("Error on adding Product into cart");
        console.error(reason);
    });
    
}

function update_cart_item(item, to_update, plus_or_minus){
    console.log("updating item ", item);
    console.log("updating object ", to_update);
    console.log("Update action %s", plus_or_minus);
    var csrfmiddlewaretoken = $('input[name="csrfmiddlewaretoken"]');
    var data = {};
    data['csrfmiddlewaretoken'] = csrfmiddlewaretoken.val();
    data['quantity'] = to_update['quantity'];
    data['action'] = to_update['action'];
    data['item'] = to_update['item_uuid'];

    var option = {
        type:'POST',
        dataType: 'json',
        url : '/cart/ajax-cart-item/' + data['item'] + '/' + data['action'] + '/',
        data : data
    }
    add_promise = ajax(option).then(function(response){
        console.log(response);
        if(response['removed']){
            to_update.parent.fadeOut('slow').remove()
        }else{
            to_update.target.val(response['item_quantity']);
            to_update.update.html(response['item_total'].replace('.', ','));
        }

        to_update.cart_total.html(response['cart_total'].replace('.', ','));
        to_update.cart_quantity.html(response['count']);
        //$("#cart-badge").text(response.count)
        document.getElementById('cart-badge').textContent = response.count;
        
    }, function(reason){
        console.error("Error on updating cart item \"%s\"",data['item']);
        console.error("Error Response Text : \"%s\"", reason.responseText)
        console.error(reason);
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


var Account = (function(){
    function Account(){
        this.is_logged = false;
    };

    Account.prototype.init = function(){
        $(".dialog-btn").click(function(event){
            var target = $(this).data('target');
            $(target).toggle();
         });
         $(".close").click(function(event){
            var target = $(this).data('target');
            $(target).hide();
         });
         var lang_form = $("#lang-form");
         var input = $("#current-lang");
         lang_form.submit(function(event){
            //event.preventDefault();
            console.log("lang-form submitted");
            return true;
         });
         $(".js-lang").click(function(event){
            var span = $(this);
            if(!span.hasClass("active")){
                console.log("span content [lang] : ");
                console.log(span.text());
                input.val(span.text());
                lang_form.submit();
            }
         });
         var login_form = $("#login-form");
         var transaction_form = $('#transaction-form');
         if(login_form.length == 0){
             console.log("no Login form found in this page");
             return;
         }
         else{
            console.log("Login form found in this page");
            login_form.submit(function(event){
                //event.preventDefault();
                var flag = false;
                console.log("Login received");
                var username = $('input[name="username"]', login_form).val();
                var password = $('input[name="password"]', login_form).val();
                var error_div = $("#error-login", login_form);
                var error_msg = "";
                if((username.length > 0) && (password.length > 0)){
                    
                    error_div.hide();
                    console.log("form : username = ", username);
                    console.log("form : password = ", password);
                    flag = true;
                }
                else{
                    error_msg = "Votre nom d'utilisateur ou votre mot est incoreecte. Veuillez verifier ces informations et essayez à nouveau."
                    console.log("form error : username or password is empty.");
                    error_div.html(error_msg).show();
                }
                return flag;
             });
         }
        if(transaction_form.length != 0){
            transaction_form.submit(function(event){
                //event.preventDefault();
                var flag = false;
                var error_div = $("#error-login", login_form);
                var error_msg = "";
                var recipient =  $('input[name="recipient"]', transaction_form).val();
                var amount =  $('input[name="amount"]', transaction_form).val();
                var details =  $('input[name="details"]', transaction_form).val();
                if((recipient.length > 0) && (details.length > 0) ){
                    if(parseInt(amount) > 0 ){
                        flag = true;
                        error_div.hide();
                    }
                    else{
                        flag = false;
                        error_msg = "Verifier les informations saisies."
                        error_div.html(error_msg).show();
                    }
                    
                }

                return flag;
            });
        }
         
         
        

         
    };

    return Account;
})();


var CardFactory = (function(){
    function CardFactory(options){
        this.required_keys = ["label", "label_attr_title", "title", "date", "amount", "initials", "initials_title", "is_seller"];
        this.default_option = options;
        this.template = $('#list-card-template');
        this.template_found = this.template.length > 0;
    }

    CardFactory.prototype.isOptionsValide = function(options){
        var flag = true;
        if(options){
            if (Object.keys(options).length < 0){
                flag = false;
            }
            else{
                flag = this.required_keys.every(function(key, index){
                    return options.hasOwnProperty(key);
                });
            }
        }
        else{
            flag = false;
        }
        return flag;
    };

    CardFactory.prototype.createCard = function(options){
        var card = null;
        if(this.isOptionsValide(options)){
            if(this.template_found){
                var $template = this.template.clone();
                $('.card-label', $template).attr('title', options.label_attr_title).html(options.label);
                $('.list-card-title', $template).html(options.title);
                $('.date', $template).html(options.date);
                $('.amount', $template).html(options.amount);
                $('.member-initials', $template).attr('title', options.initials_title).html(options.initials);
                if(options.is_seller){
                    $('.member-is-a-seller', $template).attr('title', 'Ce membre est un prestataire de services').removeClass('hide');
                }
                card = $template;
                card.removeAttr('id');
            }
            else{
                console.log('No card template could be found');
            }
            

        }
        else{
            console.log('No valid card actions');
        }
        return card;
    };

    CardFactory.prototype.default_card = function(){
        return this.createCard(this.default_option);
    }


    return CardFactory;
})();

var Transaction = (function(){
    function Transaction(){
        this.template =$("#transaction-form-wrapper.template");
        this.init();
        
    }

    Transaction.prototype.init = function(){
        this.re = RegExp('^[0-9]+$');
        var form = $('.template #transaction-form');
        console.log("Intialization transaction Form.");
        if(form.length == 0){
            console.log("transaction Form not found.");
            return;
        }
        regex = this.re;
        console.log("Found transaction Form.");
        $("#transaction-modal .modal-body").on("submit","#transaction-form", function(event){
            var form = $(this);
            var flag = true;
            event.preventDefault();
            var recipient = $("#recipient", this).val();
            var amount = 0;
            var amount_val = $("#amount", this).val();
            var description = $("#description", this).val();
            var fields = [recipient, amount_val, description];
            var errors_fields = $("#recipient-error , #amount-error , #description-error",this);
            
            fields.forEach(function(field, index){
                //console.log("Field #\n",index);
                if(field.length > 0){
                    $(errors_fields[index]).hide();
                }else{
                    //console.log("Field #", index, " is incorrect\n");
                    $(errors_fields[index]).show();
                    flag = false;
                }
            });
            if(!regex.test(amount_val)){
                $('#amount-error', this).html('Le montant doit être un numbre').show();
                console.log("the field amount must be a number");
            }
            else{
                amount = parseInt(amount_val);
            }
            if(flag){
                console.log("Recipient : ", recipient, "Amount : ", amount, "Description : ", description);
            }
            
            return flag;
        });
        
    };

    Transaction.prototype.create = function(){
        var transaction = null;
        transaction = this.template.clone().removeClass("template");
        console.log("new transaction element created");
        return transaction;
    };

    return Transaction;
})();


var CaseIssue = (function(){
    function CaseIssue(options){
        console.log("Issue construction...");
        this.template = $("#case-form-wrapper.template");
        if(options && options.selector){
            this.form_selector = options.selector;
        }
        else{
            this.form_selector = "#case-form";
        }
        console.log("Issue constructed ...");
        this.init();

    }

    CaseIssue.prototype.init = function(){
        if(this.form_selector){
            this.form = $(this.form_selector);
            if(this.form.length == 0){
                console.log("No Case Issue form found on this page");
                return;
            }
            var form = this.form;
            $(".modal .modal-body").on("submit", "#case-form",function(event){
            event.preventDefault();
            var flag = true;
            
            var $reporter = $("#reporter", this);
            var $participant = $("#participant", this);
            var $reference = $("#reference", this);
            var $description = $("#case-description", this);

            var reporter = $reporter.val();
            var participant = $participant.val();
            var reference = $reference.val();
            var description = $description.val();
            var fields = [participant, reference, description];
            var errors_fields = $("#participant-error , #reference-error , #case-description-error",this);
            
            fields.forEach(function(field, index){
                //console.log("Field #\n",index);
                if(field.length > 0){
                    $(errors_fields[index]).hide();
                }else{
                    //console.log("Field #", index, " is incorrect\n");
                    $(errors_fields[index]).show();
                    flag = false;
                }
            });
            if(flag){
                console.log("Reporter : ", reporter, " - Participant : ", participant, " - Ref : ", reference, " - Description : ", description);
            }
            else{
                console.log("The issue form contains invalid fields");
            }
            return flag;
            });
        }
        else{
            return;
        }

    };

    CaseIssue.prototype.create = function(){
        var issue = null;
        issue = this.template.clone().removeClass("template");
        console.log("new CaseIssue element created");
        return issue;
    };

    return CaseIssue;
})();


var Modal = (function(){
    function Modal(options){
        this.init();
        if(options ){
            this.transaction_factory = options.transaction_factory;
            this.factories = options.factories;
        }
        

    }


    Modal.prototype.init = function(){
        that = this;
        var trigger = $(".open-modal").click(function(event){
            var target = $($(this).data('target'));
            //console.log("opening modal ...");
            var options = {template: $(this).data('template'), modal: $(this).data('target'), factory:$(this).data('factory')};
            that.create(options);
            target.show();
        });

        $("body .modal").on("click", ".close-modal", function(event){
            //console.log("Close modal clicked");
            var target = $($(this).data('target'));
            target.hide();
            $(".modal-content .modal-body", target).empty();

        });
        if(window){
            $(window).click(function(event){
                var target = $(event.target);
                if(target.hasClass("modal")){
                    //console.log("Closing current modal");
                    target.hide();
                    $(".modal-content .modal-body", target).empty();
                }
            });
        }
    }

    Modal.prototype.create = function(options){
        var template = this.factories[options.factory].create();
        var modal = $(options.modal);
        $(".modal-content .modal-body", modal).append(template);
        //console.log("added into the modal");

    }
    return Modal;
})();


var Notify = (function(){
    function Notify(){
        this.template = $("#notify");
    }

    Notify.prototype.init = function(){
        $(".modal .modal-body").on("click", "#notify .close", function(event){
            var target = $($(this).data("target"));
            target.hide();
            $(".modal-body", target).empty();
        });

    };

    Notify.prototype.notify = function(data){
        if(data && data.hasOwnProperty('msg')){
            alert(data.msg);
        }
        else{
            alert("Notify called with wrong parameters");
        }
    };

    Notify.prototype.create = function(){

        var template = null;
        template = this.template.clone().removeClass("template");
        console.log("new Notification template element created");
        return template;
    };

    return Notify;
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
//var trans = new Transaction();
var issue_descr = "J'ai acheter un article le 23.03.2019."
" Jusqu'aujourd'hui je n'ai toujours pas recu la commande."
" Je souhaite recevoir mon article dans les plus bref delai sinon j'aimerai me faire rembourser.";

var options = {label: 'Reception', label_attr_title: 'Entrant', title: 'Reception venant de Cyrille', date: '04-05-2019', amount: 25000, initials: 'CN',initials_title: 'Cyrille Ngassam', is_seller: false};



var notify = new Notify();


function fetchTransaction(){
    $.ajax({
        url: "transactions",
        type: 'post',
        success : function(data){
            notify.notify({msg: "Nouvell Transaction sur votre compte"});
        },
        error: function(data){
            notify.notify({msg: "Error : Votre compte n'a pas pu etre actualisé"});
        },
        complete: function(data){
            setTimeout(fetchTransaction, 60000);
        }
    });
}


var Group = (function(){
    function Group(){
        this.selected_permissions = {};
        this.group_users = {}
        this.add_selected_permissions_btn = {};
        this.add_selected_users_btn = {};
        this.remove_selected_permissions_btn = {};
        this.remove_selected_users_btn = {};
        
    };

    Group.prototype.init = function(){
        $('#add-selected-users').on('click', function(event){
            event.preventDefault();
            var $target = $($(this).data('target'));
            var $source = $($(this).data('source'));
            $('option:selected', $source).appendTo($target);
            $('option', $target).prop('selected', true).addClass('selected');

        });

        $('#add-selected-permissions').on('click', function(){
            var $target = $($(this).data('target'));
            var $source = $($(this).data('source'));
            $('option:selected', $source).appendTo($target);
            $('option', $target).prop('selected', true);

        });

        $('#remove-selected-users').on('click', function(){
            var $target = $($(this).data('target'));
            var $source = $($(this).data('source'));
            $('option:selected', $source).appendTo($target);
            $('option', $target).prop('selected', true).addClass('selected');

        });

        $('#remove-selected-permissions').on('click', function(){
            var $target = $($(this).data('target'));
            var $source = $($(this).data('source'));
            $('option:selected', $source).appendTo($target);
            $('option', $target).prop('selected', true).addClass('selected');

        });
    };


    return Group;
})();


var PermissionGroupManager = (function(){
    function PermissionGroupManager(){
        this.selected_permissions = {};
        this.group_users = {}
        this.add_selected_permissions_btn = {};
        this.add_selected_users_btn = {};
        this.remove_selected_permissions_btn = {};
        this.remove_selected_users_btn = {};
        
    };

    PermissionGroupManager.prototype.init = function(){
        $('#available-permission-list').on('click','li', function(event){
            event.preventDefault();
            var $target = $('#permission-list');
            var self = $(this);
            var $selected_permissions = $('#selected-permission-list');
            $selected_permissions.append($('<option/>', {'value': self.data('value'), 'selected': true, 'text': self.text()}));
            self.appendTo($target);
        });

        $('#permission-list').on('click','li', function(event){
            event.preventDefault();
            var $target = $('#available-permission-list');
            var self = $(this);
            $('#selected-permission-list option').filter(function(){
                return this.value == self.data('value');
            }).remove();
            self.removeClass('active').appendTo($target);
        });


        $('#available-user-list').on('click','li', function(event){
            event.preventDefault();
            var $target = $('#user-list');
            var self = $(this);
            var $selected_users = $('#selected-user-list');
            $selected_users.append($('<option/>', {'value': self.data('value'), 'selected': true, 'text': self.text()}));
            self.appendTo($target);
        });

        $('#user-list').on('click','li', function(event){
            event.preventDefault();
            var $target = $('#available-user-list');
            var self = $(this);
            $('#selected-user-list option').filter(function(){
                return this.value == self.data('value');
            }).remove();
            self.removeClass('active').appendTo($target);
        });

    };


    return PermissionGroupManager;
})();

var JSFilter = (function(){
    function JSFilter(){
        console.log("creating JSFilter instance");
        this.init();
        console.log("JSFilter instance created");
    };

    JSFilter.prototype.init = function(){
        console.log("JSFilter instance initializing");
        $('.js-jsfilter-input, .js-list-filter').on('keyup', function(event){
            event.stopPropagation();
            var value = this.value.trim();
            var target_container = this.getAttribute('data-target');
            var el = this.getAttribute('data-element');
            $(target_container + " " +  el).filter(function(){
                $(this).toggle(this.innerHTML.includes(value));
            });
        });

        console.log("JSFilter instance initialized");
    };


    return JSFilter;
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
    div.append([label_name, label_display_name, label_value, label_value_type, input_form_id, delete_button]);
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
        this.replace_pattern = /\d+/g;
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
        var label_value = $("<label/>").text(attr_template.value + " : ");
        var input_value = $('<input type="text">').attr({
            'id':`id-form-${this.total_form}-value`,
            'name': `form-${this.total_form}-value`,
            'maxlength': input_max_length
        });
        input_value.appendTo(label_value);
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
        div.append([label_name, label_display_name, label_value, label_value_type, input_form_id, delete_button]);
        div.appendTo(container);
        self.incremente_management_form();
        self.attrs_inputs.push([input_name, input_display_name, input_value, select_value_type, input_form_id]);
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

var id_form_TOTAL_FORMS;
var id_form_INITIAL_FORMS;
var id_form_MIN_NUM_FORMS;
var id_form_MAX_NUM_FORMS;
var formset_prefix = 'form';
var total_form = 0;
var input_max_length = 32;
var attr_list = [];
var replace_pattern = /\d+/g;

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
    var input_form_id = $('<input type="hidden">').attr({
        'id':`id-form-${total_form}-id`,
        'name': `form-${total_form}-id`,
    });
    div.append([label_name, label_display_name, label_value, label_value_type, input_form_id, delete_button]);
    attr_list.push([input_name, input_display_name, input_value, select_value_type, input_form_id]);
    div.appendTo(container);
    incremente_management_form(form);
    console.log("[OK] Adding attribute done!");
    return div;
}


$(document).ready(function(){
let account = new Account();
account.init();
var notifications = new Notification();
notifications.init();
let tabs = new Tabs();
tabs.init();

var jsfilter = new JSFilter();

var filter = new TableFilter();
filter.init();

var permissionManager = new PermissionGroupManager();

var group = new Group();
permissionManager.init();
group.init();
//$(window).on('beforeunload', onbeforeunload);
window.addEventListener('beforeunload', askConfirmation);
var scheduled_query = false;
var query_delay = 800;
var $user_search_result = $('#user-search-result');
var $user_search_target = $($user_search_result.data('target'));
var $user_search_target_name = $($user_search_result.data('target-name'));

var userSearch = function(options){

    var promise = ajax(options).then(function(response){
        //console.log("User Search succeed");
        //console.log(response);
        $user_search_result.empty();
        response.forEach(function(user, index){
            var full_name = user.first_name + " " +  user.last_name;
            $('<li>').data('user-id', user.id).data('user-name', full_name).html(full_name + " [" + user.username + "]").
            on('click', function(event){
                event.stopPropagation();
                var user_id = $(this).data('user-id');
                var user_name = $(this).data('user-name');
                $user_search_target.val(user_id);
                //$(".js-user-search").val(user_name);
                $user_search_target_name.val(user_name);
                $user_search_result.hide();
                $user_search_result.empty();
            }).appendTo($user_search_result);
            $user_search_result.show();
        });

    }, function(error){
        console.log("User Search failed");
        console.log(error);
    });
}

$('.js-user-search').on('keyup', function(event){
    event.stopPropagation();
    var query = $(this).val();
    query = query.trim()
    if(query.length == 0 ){
        return;
    }
    var options = {
        url:'/api/user-search/',
        type: 'GET',
        data : {'search': query},
        dataType: 'json'
    };
    if(scheduled_query){
        clearTimeout(scheduled_query);
    }
    scheduled_query = setTimeout(userSearch, query_delay, options);
});

$('.js-table-update').on('click', function(event){
    console.log("Updating the Table");
});
$('.js-table-next').on('click', function(event){
    console.log("Displaying the next %s row of the Table", filter.rowStep);
    filter.next();
    
});

$('.js-table-previous').on('click', function(event){
    console.log("Displaying the next %s row of the Table", filter.rowStep);
    filter.previous();
    
});
let slider = new Slider();
slider.init();
    var factory = new CardFactory(options);
    var list = $('.list-cards');
    var transaction = new Transaction();
    var cases = new CaseIssue();
    var collapsible = new Collapsible();
    collapsible.init();
    
    var modal = new Modal({transaction_factory: transaction, factories: {transaction : transaction, cases : cases, notify : notify}});

    //setTimeout(fetchTransaction, 60000);
    $('.js-add-another').click(function(event){
        var card = factory.default_card();
        if(card != null){
            card.appendTo(list).addClass('list-card').hide().fadeIn(600);
            console.log("Added new card");
        }
        else{
            console.log("Card not created");
        }
    });

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
    $('.js-user-selector').on('click', 'li', function(){
        let target = $(this);
        $('#members').append($('<option/>', {'value': target.data('id'), 'selected': true, 'text': target.text()}));
        target.appendTo('#selected-members');
    });
    $('#selected-members').on('click', 'li', function(){
        let target = $(this);
        target.appendTo('.js-user-selector');
        $('#members option').filter(function(){
            return this.value == target.data('id');
        }).remove();
        
    });

    $('.mat-list').on('click', '.mat-list-item', function(){
        $(this).toggleClass('active');
    });

    $('.js-dialog-open').on('click', function(){
        var target = $($(this).data('target'));
        target.show();
    });

    $('.js-dialog-close').on('click', function(){
        var parent = $(this).parents('.dialog').hide();
        $('input[type!="hidden"]', parent).val('');
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
    $('.js-add-to-cart').on('click', function(event){
        var target = $(event.target);
        var product = {
            id : target.data('id'),
            name: target.data('name'),
            quantity : target.data('quantity')
        }
        add_to_cart(product);
    });

    $('#add-cart-form').submit(function(event){
        console.log("submiting cart form");
        event.preventDefault();
        form_submit_add_cart();
    });

    $('.js-add-new-attribute').on('click', function(){
        var target = $($(this).data('target'));
        var form_container = $($(this).data('form'));
        create_attribute_entry(target, form_container);
    });

    var selectable_list = $(".js-selectable");
    var activable_list = $(".js-activable");
    var select_all = $('.js-select-all');
    selectable_list.on('click', function(){
        var is_selected = selectable_list.is(function (el) {
            return this.checked;
        });
        
        var selected_all = selectable_list.is(function (el) {
            return !this.checked;
        });
        select_all.prop('checked', !selected_all);
        activable_list.prop('disabled', !is_selected);
    });

    select_all.on('click', function(){
        console.log("Select All clicked : %s", this.checked);
        selectable_list.prop('checked', this.checked);
        activable_list.prop('disabled', !this.checked);
    });

    $('.js-cart-update-item-quantity,.js-cart-delete-item').on('click', function(){
        var item = $(this);
        var obj = {};
        obj['action'] = item.data('action');
        obj['target'] = $('#' + item.data('target'));
        obj['update'] = $('#' + item.data('update'));
        obj['parent'] = $('#' + item.data('parent'));
        obj['cart_total'] = $('.js-cart-total');
        obj['cart_quantity'] = $('.js-cart-quantity');
        obj['item_uuid'] = item.data('item');
        var plus_or_minus = item.data('action') == "increment";
        update_cart_item(item, obj, plus_or_minus);
    });
    
});


