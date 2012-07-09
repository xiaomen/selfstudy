// Picker

!function( $ ) {
    var Picker = function(element, html) {
        this.element = $(element);
        console.log(this.element.offset()); 
        this.picker = $(ZPGlobal.template.replace("{{ html }}", html)).appendTo('body').on('mousedown',$.proxy(this.mousedown, this)).on('click',$.proxy(this.click, this));
        this.component = this.element.is('.date') ? this.element.find('.add-on') : false;

        this.isInput = this.element.is('input');
        
        if (this.isInput) {
            this.element.on({
                focus: $.proxy(this.show, this),
                click: $.proxy(this.show, this),
                blur: $.proxy(this.blur, this),
                keyup: $.proxy(this.update, this),
                keydown: $.proxy(this.keydown, this)
            });
        }
    }; 

    Picker.prototype = {
        constructor: Picker, 

        show: function(e) {
            this.picker.show(); 
            this.height = this.component ? this.component.outerHeight() : this.element.outerHeight();
            this.place();
			$(window).on('resize', $.proxy(this.place, this));
			$('body').on('click', $.proxy(this.hide, this));
			if (e) {
				e.stopPropagation();
				e.preventDefault();
			}
			if (!this.isInput) {
				$(document).on('mousedown', $.proxy(this.hide, this));
			}
        }, 

		place: function() {
			var offset = this.component ? this.component.offset() : this.element.offset();
			this.picker.css({
				top: offset.top + this.height,
				left: offset.left
			});
		},

        hide: function() {
      		this.picker.hide();
            $(window).off('resize', this.place);
			if (!this.isInput) {
				$(document).off('mousedown', this.hide);
			}
			$('body').off('click',$.proxy(this.click, this));
            oninputchanging(); 
        }, 

        blur: function() {
        }, 
    }; 

    $.fn.picker = function(html) {
        return this.each(function() {
            var $this = $(this), 
               data = $this.data("picker"); 
            if(!data) {
                $this.data('picker', (data = new Picker(this, html))); 
            }
        }); 
    }; 
    var ZPGlobal = {
    }; 
    ZPGlobal.template = '<div class="datepicker dropdown-menu lessonpicker" style="min-width:200px;">'+
                        '{{ html }}'+
                        '</div>';
}( window.jQuery ); 
