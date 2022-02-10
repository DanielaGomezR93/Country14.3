# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _, http
import werkzeug
from odoo.http import request
from odoo.addons.website_event_sale.controllers.main import WebsiteEventSaleController
from odoo.addons.website_event.controllers.main import WebsiteEventController
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)

class WebsiteEventControllerExtend(WebsiteEventController):

    def _prepare_event_register_values(self, event, **post):
        urls = event._get_event_resource_urls()
        user_id = request.env['res.users'].search([('id', '=', request.env.context.get('uid'))])
        cfr_search = request.env['frecuent.partner.relation'].search([('partner_id', '=', user_id.partner_id.id)])
        cf = []
        for x in cfr_search:
            val = {
                'prefix_vat': x.frecuent_partner_id.prefix_vat,
                'vat': x.frecuent_partner_id.vat,
                'email': x.frecuent_partner_id.email,
                'phone': x.frecuent_partner_id.phone,
                'name': x.frecuent_partner_id.name,
                'active': x.active,
        
            }
            cf.append(val)
        return {
            'event': event,
            'valid': True,
            'msg': '',
            'main_object': event,
            'range': range,
            'google_url': urls.get('google_url'),
            'iCal_url': urls.get('iCal_url'),
            'contacts': cf,
        }

    def _create_attendees_from_registration_post(self, event, registration_data):
        """ Also try to set a visitor (from request) and
        a partner (if visitor linked to a user for example). Purpose is to gather
        as much informations as possible, notably to ease future communications.
        Also try to update visitor informations based on registration info. """
        visitor_sudo = request.env['website.visitor']._get_visitor_from_request(force_create=True)
        visitor_sudo._update_visitor_last_visit()
        visitor_values = {}
        _logger.info('_create_attendees_from_registration_post')
        _logger.info(self)
        _logger.info(event)
        _logger.info(registration_data)
        registrations_to_create = []
        for registration_values in registration_data:
            if 'event_ticket_id' in list(registration_values.keys()):
                registration_values['event_id'] = event.id
                if not registration_values.get('partner_id') and visitor_sudo.partner_id:
                    registration_values['partner_id'] = visitor_sudo.partner_id.id
                elif not registration_values.get('partner_id'):
                    registration_values['partner_id'] = request.env.user.partner_id.id
            
                if visitor_sudo:
                    # registration may give a name to the visitor, yay
                    if registration_values.get('name') and not visitor_sudo.name and not visitor_values.get('name'):
                        visitor_values['name'] = registration_values['name']
                    # update registration based on visitor
                    registration_values['visitor_id'] = visitor_sudo.id
            
                registrations_to_create.append(registration_values)
    
        if visitor_values:
            visitor_sudo.write(visitor_values)
    
        return request.env['event.registration'].sudo().create(registrations_to_create)


class WebsiteEventSaleControllerExtend(WebsiteEventSaleController):

    def valid(self, date1, partner, registrations, event):
        _logger.info('VALID')
        _logger.info('EVENTO')
        _logger.info(self)
        _logger.info('PARTNER')
        _logger.info(partner)
        ticket = ''
        count_reg = 0
        partner_id = request.env['res.partner'].search(
            [('id', '=', partner)])
        _logger.info('PARTNER ID')
        _logger.info(partner)
        if partner_id.can_access_club is False:
            _logger.info('NO ESTA SOLVENTE')
            _logger.info('NO ESTA SOLVENTE')
            _logger.info('NO ESTA SOLVENTE')
            _logger.info('NO ESTA SOLVENTE')
            _logger.info('NO ESTA SOLVENTE')
            _logger.info('NO ESTA SOLVENTE')
            return False
        else:
            _logger.info('SI ESTA SOLVENTE')
            _logger.info('SI ESTA SOLVENTE')
            _logger.info('SI ESTA SOLVENTE')
            _logger.info('SI ESTA SOLVENTE')
            _logger.info('SI ESTA SOLVENTE')
            _logger.info('SI ESTA SOLVENTE')
        for cr in registrations:
            if 'event_ticket_id' in list(cr.keys()):
                ticket = cr.get('event_ticket_id')
        if event[0].event_type == 'invitations':
            len_entries_day = request.env['event.registration'].search(
                [('date_invitation', '=', date1),
                 ('partner_id', '=', partner),
                 ('state', 'not in', ['cancel'])])
            _logger.info('EL PARTNER HA INVITADO %s PERSONAS AL CLUB EN EL DIA' % len(len_entries_day))
            qty_max_to_day = int(request.env['ir.config_parameter'].sudo().get_param('qty_max_to_day'))
            _logger.info('LA CANT PERMITIDA POR DIA ES DE %s INVITADOS' % qty_max_to_day)
            for cr in registrations:
                if 'event_ticket_id' in list(cr.keys()):
                    count_reg += 1
                    _logger.info(cr)
            _logger.info('EL PARTNER ESTA REGISTRANDO %s PERSONAS AL CLUB EN EL DIA' % count_reg)
            entries_day = len(len_entries_day) + count_reg
            if entries_day > qty_max_to_day:
                _logger.info('EL PARTNER SUPERA LA CANTIDAD DE INVITACIONES')
                return False
            date_parameter = datetime.strptime(str(date1), '%Y-%m-%d')
            date_start_date = '%s-%s-%s' % (date_parameter.year, date_parameter.month, 1)
            if date_parameter.month != 12:
                date_end_date = '%s-%s-%s' % (date_parameter.year, date_parameter.month + 1, 1)
            else:
                date_end_date = '%s-%s-%s' % (date_parameter.year, date_parameter.month, 31)
            qty_max_to_mounth = int(request.env['ir.config_parameter'].sudo().get_param('qty_max_to_mounth'))
            _logger.info('LA CANT PERMITIDA POR MES ES DE %s INVITADOS' % qty_max_to_mounth)
            for x in registrations:
                if 'event_ticket_id' in list(x.keys()):
                    len_entries_mounth = request.env['event.registration'].search(
                        [('date_invitation', '>=', date_start_date),
                         ('date_invitation', '<', date_end_date),
                         ('partner_id', '=', partner),
                         ('vat', '=', x['vat']),
                         ('state', 'not in', ['cancel']),
                         ])
                    entries_mounth = len(len_entries_mounth) + 1
                    _logger.info('EL INVITADO A INGRESADO %s VECES AL CLUB EN EL MES' % len(len_entries_mounth))
                    if entries_mounth > qty_max_to_mounth:
                        _logger.info('EL PARTNER SUPERA LA CANTIDAD DE INVITACIONES AL MES')
                        return False
                    else:
                        return True
        return True

    """@http.route()
    def registration_confirm(self, event, **post):
        order = request.website.sale_get_order(force_create=1)
        attendee_ids = set()
        valid = False
        registrations = self._process_registration_details(post)
        user_id = request.env['res.users'].search([('id', '=', request.env.context.get('uid'))])
        valid = self.valid(registrations[0].get('date_invitation'), user_id.partner_id.id, registrations)
        if valid:
            for registration in registrations:
                if 'ticket_id' in list(registration.keys()):
                    if 'contact' in list(registration.keys()):
                        cfr_search = False
                        fp = False
                        cf_search = request.env['frecuent.partner'].search([('vat', '=', registration['vat'])])
                        if cf_search:
                            cfr_search = request.env['frecuent.partner.relation'].search(
                                [('frecuent_partner_id', '=', cf_search.id),
                                 ('partner_id', '=', user_id.partner_id.id)])
                        if not cf_search:
                            cf = {
                                'prefix_vat': registration['prefix_vat'],
                                'vat': registration['vat'],
                                'email': registration['email'],
                                'phone': registration['phone'],
                                'name': registration['name'],
                            }
                            fp = request.env['frecuent.partner'].create(cf)
                        if not cfr_search and not cf_search:
                            cf_related = {
                                'active': True,
                                'frecuent_partner_id': fp.id,
                                'partner_id': user_id.partner_id.id,
                            }
                            request.env['frecuent.partner.relation'].create(cf_related)
                        elif not cfr_search and cf_search:
                            cf_related = {
                                'active': True,
                                'frecuent_partner_id': cf_search.id,
                                'partner_id': user_id.partner_id.id,
                            }
                            request.env['frecuent.partner.relation'].create(cf_related)
                        elif cfr_search and cf_search:
                            cfr_search.write({'active': True})
                    else:
                        print('NO ES FRECUENTE')
                    if not order.validity_date:
                        order.write({'validity_date': registration['date_invitation']})
                    ticket = request.env['event.event.ticket'].sudo().browse(int(registration['ticket_id']))
                    cart_values = order.with_context(event_ticket_id=ticket.id, fixed_price=True)._cart_update(
                        product_id=ticket.product_id.id, add_qty=1, registration_data=[registration])
                    attendee_ids |= set(cart_values.get('attendee_ids', []))
                else:
                    if registration['name'] == '':
                        user_id = request.env['res.users'].search([('id', '=', request.env.context.get('uid'))])
                        print('USER')
                        print(user_id.partner_id.id)
                        partner_frec_id = request.env['frecuent.partner'].search([('vat', '=', registration['vat'])]).id
                        print('Partner_frec')
                        print(partner_frec_id)
                        relation = request.env['frecuent.partner.relation'].search(
                            [('partner_id', '=', user_id.partner_id.id), ('frecuent_partner_id', '=', partner_frec_id)])
                        print('relation update')
                        print(relation)
                        relation.write({'active': False})
                    else:
                        partner_frec_id = request.env['frecuent.partner'].search([('vat', '=', registration['vat'])])
                        partner_frec_id.write({
                            'name': registration['name'],
                            'email': registration['email'],
                            'phone': registration['phone'],
                        })
            # free tickets -> order with amount = 0: auto-confirm, no checkout
            if not order.amount_total:
                order.action_confirm()  # tde notsure: email sending ?
                attendees = request.env['event.registration'].browse(list(attendee_ids)).sudo()
                # clean context and session, then redirect to the confirmation page
                request.website.sale_reset()
                urls = event._get_event_resource_urls(list(attendee_ids))
                return request.render("website_event.registration_complete", {
                    'attendees': attendees,
                    'event': event,
                    'google_url': urls.get('google_url'),
                    'iCal_url': urls.get('iCal_url')
                })

            return request.redirect("/shop/checkout")
        else:
            is_solvent = self.can_access_club(user_id.partner_id.id)
            if is_solvent is False:
                msg = 'Debe estar solvente para registrar invitaciones!!!'
            else:
                msg = 'No puede registrar mas invitados de los permitidos por el club.!!!'
            values = {
                'event': event,
                'valid': False,
                'main_object': event,
                'msg': msg,
                'range': range,
                'registrable': event.sudo()._is_event_registrable()
            }
            return request.render("website_event.event_description_full", values)"""

    def _process_attendees_form(self, event, form_details):
        
        """ Process data posted from the attendee details form.

        :param form_details: posted data from frontend registration form, like
            {'1-name': 'r', '1-email': 'r@r.com', '1-phone': '', '1-event_ticket_id': '1'}
        """
        _logger.info('_process_attendees_form')
        allowed_fields = request.env['event.registration']._get_website_registration_allowed_fields()
        registration_fields = {key: v for key, v in request.env['event.registration']._fields.items() if
                               key in allowed_fields}
        registrations = {}
        global_values = {}
        for key, value in form_details.items():
            counter, attr_name = key.split('-', 1)
            field_name = attr_name.split('-')[0]
            if field_name not in registration_fields:
                continue
            elif isinstance(registration_fields[field_name], (fields.Many2one, fields.Integer)):
                value = int(value) or False  # 0 is considered as a void many2one aka False
            else:
                value = value
        
            if counter == '0':
                global_values[attr_name] = value
            else:
                registrations.setdefault(counter, dict())[attr_name] = value
        for key, value in global_values.items():
            for registration in registrations.values():
                registration[key] = value
    
        return list(registrations.values())

    @http.route(['''/event/<model("event.event"):event>/registration/confirm'''], type='http', auth="public",
                methods=['POST'], website=True)
    def registration_confirm(self, event, **post):
        if not event.can_access_from_current_website():
            raise werkzeug.exceptions.NotFound()
        _logger.info('registration_confirm')
        _logger.info(self)
        _logger.info(event)
        _logger.info(post)
        registrations = self._process_attendees_form(event, post)
        _logger.info(registrations)
        valid = False
        user_id = request.env['res.users'].search([('id', '=', request.env.context.get('uid'))])

        valid = self.valid(registrations[0].get('date_invitation'), user_id.partner_id.id, registrations, event)
        _logger.info('is valid %s' % valid)
        if valid:
            for registration in registrations:
                if 'event_ticket_id' in list(registration.keys()):
                    if 'contact' in list(registration.keys()):
                        print('ES FRECUENTE3')
                        cfr_search = False
                        fp = False
                        cf_search = request.env['frecuent.partner'].search([('vat', '=', registration['vat'])])
                        if cf_search:
                            cfr_search = request.env['frecuent.partner.relation'].search(
                                [('frecuent_partner_id', '=', cf_search.id),
                                 ('partner_id', '=', user_id.partner_id.id)])
                        if not cf_search:
                            cf = {
                                'prefix_vat': registration['prefix_vat'],
                                'vat': registration['vat'],
                                'email': registration['email'],
                                'phone': registration['phone'],
                                'name': registration['name'],
                            }
                            fp = request.env['frecuent.partner'].create(cf)
                        if not cfr_search and not cf_search:
                            cf_related = {
                                'active': True,
                                'frecuent_partner_id': fp.id,
                                'partner_id': user_id.partner_id.id,
                            }
                            request.env['frecuent.partner.relation'].create(cf_related)
                        elif not cfr_search and cf_search:
                            cf_related = {
                                'active': True,
                                'frecuent_partner_id': cf_search.id,
                                'partner_id': user_id.partner_id.id,
                            }
                            request.env['frecuent.partner.relation'].create(cf_related)
                        elif cfr_search and cf_search:
                            cfr_search.write({'active': True})
                    else:
                       print('NO ES FRECUENTE2')
                else:
                    if registration['name'] == '':
                        user_id = request.env['res.users'].search([('id', '=', request.env.context.get('uid'))])
                        print('USER')
                        print(user_id.partner_id.id)
                        partner_frec_id = request.env['frecuent.partner'].search([('vat', '=', registration['vat'])]).id
                        print('Partner_frec')
                        print(partner_frec_id)
                        relation = request.env['frecuent.partner.relation'].search(
                            [('partner_id', '=', user_id.partner_id.id), ('frecuent_partner_id', '=', partner_frec_id)])
                        print('relation update')
                        print(relation)
                        relation.write({'active': False})
                    else:
                        partner_frec_id = request.env['frecuent.partner'].search([('vat', '=', registration['vat'])])
                        partner_frec_id.write({
                            'name': registration['name'],
                            'email': registration['email'],
                            'phone': registration['phone'],
                        })
            attendees_sudo = self._create_attendees_from_registration_post(event, registrations)
        
            return request.render("website_event.registration_complete",
                                  self._get_registration_confirm_values(event, attendees_sudo))
        else:
            _logger.info('NO VALIDO')
            is_solvent = self.can_access_club(user_id.partner_id.id)
            if is_solvent is False:
                msg = 'Debe estar solvente para registrar invitaciones!!!'
            else:
                msg = 'No puede registrar mas invitados de los permitidos por el club.!!!'
            values = {
                'event': event,
                'valid': False,
                'main_object': event,
                'msg': msg,
                'range': range,
            }
            return request.render("website_event.event_description_full", values)


    def can_access_club(self, partner):
        partner_id = request.env['res.partner'].search(
            [('id', '=', partner)])
        if partner_id.can_access_club is False:
            return False
        else:
            return True
