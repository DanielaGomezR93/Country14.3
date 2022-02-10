# -*- coding: utf-8 -*-
from odoo import models, api
from odoo.http import request


class CustomerBadge(models.AbstractModel):
    _name = 'report.country_qr_code.customer_qr_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data['type'] == 'cust':
            dat = [request.env['res.partner'].browse(data['data'])]
            return {
                'data': dat,
            }


class CustomerBadgeInvitation(models.AbstractModel):
    _name = 'report.country_qr_code.customer_qr_invitation_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        if data['type'] == 'cust':
            dat = [request.env['event.registration'].browse(data['data'])]
            return {
                'data': dat,
            }
