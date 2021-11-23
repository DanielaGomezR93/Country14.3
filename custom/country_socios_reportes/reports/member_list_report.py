# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date


class ReportMemberList2(models.AbstractModel):
	_name = 'report.country_socios_reportes.member_list2'

	@api.model
	def _get_report_values(self, docids, data=None):
		if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
			raise UserError(_("Form content is missing, this report cannot be printed."))
		print("data context",data.get('context'))
		ctx = data.get('context',False)
		name_user = ''
		if ctx:
			uid = ctx.get('uid')
			obj_uid = self.env['res.users'].sudo().search([('id','=',uid)])
			if obj_uid:
				name_user = obj_uid.name
		form = data.get('form',False)
		if not form:
			raise UserError("Error en formulario de reporte")
		print("form",form)
		state_partner = form.get('status',False)
		state_action = form.get('state_action',False)
		search_domain = []
		if state_partner and state_partner != 'all':
			search_domain += [('state_partner','=',state_partner)]

		if state_action and state_action != 'all':
			search_domain += [('state_action','=',state_action)]
		search_domain += [('active', '=', True),('parent_id','=',False),('customer_rank','>',0),('action_number','!=',False)]#solo socios y asociados
		
		docs = self.env['res.partner'].sudo().search(search_domain)

		return {
			'data': data['form'],
			'docs': docs,
			'date':date.today(),
			'name_user':name_user,
		}
