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
                $modal.on('click', '.delete-cf', function (clicked) {
                    console.log('Pasoooo');
                    console.log(clicked.target.getAttribute('name'));
                    let $button_select = clicked.target.getAttribute('name').toString().slice(0, 1);
                    let $value_select = clicked.target.getAttribute('name').toString().slice(1,);
                    $("div[name=f" + $value_select.toString().concat('-div') + "]").hide();
                    $("input[name=f" + $value_select.toString().concat('-name') + "]").val('');

                });
                $modal.on('click', '.save-cf', function (clicked) {
                    console.log('Pasoooo');
                    console.log(clicked.target.getAttribute('name'));
                    let $button_select = clicked.target.getAttribute('name').toString().slice(0, 1);
                    let $value_select = clicked.target.getAttribute('name').toString().slice(1,);
                    //$("div[name=f" + $value_select.toString().concat('-div') + "]").hide();
                    $("input[name=a" + $value_select.toString().concat('-operation') + "]").val('save');

                });
                $modal.on('click', '.selection-cf', function (clicked) {
                    console.log('Pasoooo');
                    console.log(clicked.target.getAttribute('name'));
                    let $button_select = clicked.target.getAttribute('name').toString().slice(0, 1);
                    let $value_select = clicked.target.getAttribute('name').toString().slice(1,);
                    //let $f = 'f'.concat($value_select,'-vat');
                    let $r = $value_select.concat('-vat');

                    let $prefix_vat_select = $("input[name=" + 'f'.concat($value_select,'-prefix_vat') + "]").val();
                    let $vat_select = $("input[name=" + 'f'.concat($value_select,'-vat') + "]").val();
                    let $name_select = $("input[name=" + 'f'.concat($value_select,'-name') + "]").val();
                    let $email_select = $("input[name=" + 'f'.concat($value_select,'-email') + "]").val();
                    let $phone_select = $("input[name=" + 'f'.concat($value_select,'-phone') + "]").val();


                    //$vat_register = $("input[name=" + $r + "]").val($vat_select);
                    console.log('button selected');
                    console.log($button_select);
                    console.log('value selected');
                    console.log($value_select);
                    console.log('Buscar para');
                    //console.log($f);
                    console.log('Input prefix_vat');
                    console.log($prefix_vat_select);
                    console.log('Input vat');
                    console.log($vat_select);
                    console.log('Input name');
                    console.log($name_select);
                    console.log('Input email');
                    console.log($email_select);
                    console.log('Input phone');
                    console.log($phone_select);

                    var $iter = 1;
                    var $insert = false;
                    while ($iter < 10) {
                        if ($insert == false) {
                            console.log('NO INSERTADO');
                            if ($("input[name=" + $iter.toString().concat('-vat') + "]").val() == '') {
                                console.log('insertando');
                                $("input[name=" + $iter.toString().concat('-vat') + "]").val($vat_select);
                                $("input[name=" + $iter.toString().concat('-name') + "]").val($name_select);
                                $("input[name=" + $iter.toString().concat('-email') + "]").val($email_select);
                                $("input[name=" + $iter.toString().concat('-phone') + "]").val($phone_select);
                                $insert = true;
                                $iter = 10;
                            }
                        }
                        $iter++;
                    }

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
