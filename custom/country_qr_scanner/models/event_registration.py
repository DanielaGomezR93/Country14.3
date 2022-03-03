# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
import logging
_logger = logging.getLogger(__name__)


class EventRegistationScannner(models.Model):
    _inherit = 'event.registration'
    
    @api.model
    def _patameter_state_registration_event(self, code):
        """
            :param : codigo del qr
            :return: estado del invitado, ...]
        """
        result = ""
        if code:
            search_type = code.find("INV")
            search_fecha = code.find("FEC")
            code_id = code[:search_type]
            code_type = code[search_type:search_type+3]
            code_ci = code[search_type+3:search_fecha]
            code_date = code[search_fecha+3:]
            _logger.info(code_id)
            _logger.info(code_type)
            _logger.info(code_ci)
            _logger.info(code_date)
            data = self.env['event.registration'].search(
                [('id', '=', code_id), ('vat', '=', code_ci), ('date_invitation', '=', code_date),], limit=1)
            if data.id:
                result = data
        return result

    date_scanned = fields.Datetime('Fecha de escaneo')
