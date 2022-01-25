odoo.define('country_eventos.website_event', function (require) {

var ajax = require('web.ajax');
var core = require('web.core');
var Widget = require('web.Widget');
var publicWidget = require('web.public.widget');

var _t = core._t;

// Catch registration form event, because of JS for attendee details
var EventRegistrationForm = Widget.extend({

    /**
     * @override
     */
    start: function () {
        var self = this;
        console.log('Cargado este archivo');
        var res = this._super.apply(this.arguments).then(function () {
            $('#registration_form .a-submit')
                .off('click')
                .click(function (ev) {
                    self.on_click(ev);
                });
        });
        return res;
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {Event} ev
     */
    on_click: function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        var $form = $(ev.currentTarget).closest('form');
        var $button = $(ev.currentTarget).closest('[type="submit"]');
        var post = {};
        console.log('Pasoooo1');
        $('#registration_form table').siblings('.alert').remove();
        $('#registration_form select').each(function () {
            post[$(this).attr('name')] = $(this).val();
        });
        var tickets_ordered = _.some(_.map(post, function (value, key) { return parseInt(value); }));
        if (!tickets_ordered) {
            console.log('Pasoooo21');
            $('<div class="alert alert-info"/>')
                .text(_t('Please select at least one ticket.'))
                .insertAfter('#registration_form table');
            return new Promise(function () {});
        } else {
            console.log('Pasoooo22');
            $button.attr('disabled', true);
            return ajax.jsonRpc($form.attr('action'), 'call', post).then(function (modal) {
                var $modal = $(modal);
                $modal.modal({backdrop: 'static', keyboard: false});
                $modal.find('.modal-body > div').removeClass('container'); // retrocompatibility - REMOVE ME in master / saas-19
                $modal.appendTo('body').modal();
                $modal.on('click', '.js_goto_event', function () {
                    alert('ENVIAR');
                    $modal.modal('hide');
                    $button.prop('disabled', false);
                });
                $modal.on('click', '.clear-item', function (clicked) {
                    console.log('Pasoooo');
                    console.log(clicked.target.getAttribute('name'));
                    let $button_select = clicked.target.getAttribute('name').toString().slice(0, 1);
                    let $value_select = clicked.target.getAttribute('name').toString().slice(1,);
                    $("input[name=" + $value_select.toString().concat('-vat') + "]").val('');
                    $("input[name=" + $value_select.toString().concat('-name') + "]").val('');
                    $("input[name=" + $value_select.toString().concat('-email') + "]").val('');
                    $("input[name=" + $value_select.toString().concat('-phone') + "]").val('');

                });
                $modal.on('click', '.close', function () {
                    $button.prop('disabled', false);
                });
            });
        }
    },
});

publicWidget.registry.EventRegistrationFormInstance = publicWidget.Widget.extend({
    selector: '#registration_form',

    /**
     * @override
     */
    start: function () {
        var def = this._super.apply(this, arguments);
        this.instance = new EventRegistrationForm(this);
        return Promise.all([def, this.instance.attachTo(this.$el)]);
    },
    /**
     * @override
     */
    destroy: function () {
        this.instance.setElement(null);
        this._super.apply(this, arguments);
        this.instance.setElement(this.$el);
    },
});

return EventRegistrationForm;
});
