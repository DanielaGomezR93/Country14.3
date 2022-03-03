# -*- coding: utf-8 -*-

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None
from io import BytesIO

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class Partners(models.Model):
    _inherit = 'res.partner'

    qr_code = fields.Char(string="QR Code", readonly=True)
    qr = fields.Binary(string="QR Imagen")
    qr_end_date = fields.Date('Vencimiento de Qr', default=fields.Date.context_today,
                              help='Fecha para borrar el codigo qr')

    def generate_qr(self):
        if qrcode and base64:
            for record in self:
                if not self.qr_code:
                    prefix = str(
                        record.env['ir.config_parameter'].sudo().get_param('country_qr_code.config.customer_prefix'))
                    if not prefix:
                        raise UserError(_('Establece un prefijo de cliente en la configuración general'))
                    record.qr_code = prefix + record.vat.upper() + "-" + str(record.id)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.qr_code)
                qr.make(fit=True)

                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                record.write({'qr': qr_image})
                return record.env.ref('country_qr_code.print_qr').report_action(record, data={'data': record.id,
                                                                                              'type': 'cust'})
            else:
                raise UserError(_('No se cumplen los requisitos necesarios para ejecutar esta operación'))

    def clear_qr(self):
        for record in self:
            record.write({'qr_code': False, 'qr': False})


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    customer_prefix = fields.Char(string="Customer QR Prefix")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        customer_prefix = self.env["ir.config_parameter"].get_param("country_qr_code.config.customer_prefix")
        res.update({
            'customer_prefix': customer_prefix if type(customer_prefix) else False,
        }
        )
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('country_qr_code.config.customer_prefix', self.customer_prefix)
        
        
class EventRegistrationCqc(models.Model):
    _inherit = 'event.registration'

    qr_code = fields.Char(string="Código QR", readonly=True)
    qr = fields.Binary(string="Imágen QR")
    qr_end_date = fields.Date('Vencimiento de Qr', default=fields.Date.context_today,
                              help='Fecha para borrar el codigo qr')

    def generate_qr(self):
        if qrcode and base64:
            for record in self:
                if not self.qr_code:
                    prefix = 'INV'
                    record.qr_code = str(record.id) + str(prefix) + record.vat.upper() + "FEC" + str(record.date_invitation)
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.qr_code)
                qr.make(fit=True)

                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())
                record.write({'qr': qr_image})
                return record.env.ref('country_qr_code.print_qr_invitation').report_action(record, data={'data': record.id,
                                                                                              'type': 'cust'})
            else:
                raise UserError(_('No se cumplen los requisitos necesarios para ejecutar esta operación'))

    def clear_qr(self):
        for record in self:
            record.write({'qr_code': False, 'qr': False})
