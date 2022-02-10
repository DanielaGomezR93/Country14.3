# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


class ResPartnerScannner(models.Model):
    _inherit = 'res.partner'
    
    @api.model
    def _patameter_state_partner(self, code):
        """
            :param : codigo del qr
            :return: estado del socio, ...]
        """
        result = ""
        if code:
            code_separator = code.find("-")
            code_prefix = str(
                        self.env['ir.config_parameter'].sudo().get_param('country_qr_code.config.customer_prefix'))
            ci = code[len(code_prefix):code_separator]
            id_partner = code[code_separator+1:]
            data = self.env['res.partner'].search(
                [('id', '=', id_partner), ('vat', '=', ci)], limit=1)
            if data.id:
                result = data
        return result
