# -*- coding: utf-8 -*-

from odoo import api, fields, exceptions, http, models, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import xlsxwriter

from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception,content_disposition
from io import BytesIO
import logging
import time

from collections import OrderedDict
import pandas as pd

_logger = logging.getLogger(__name__)


class WizardMemberList(models.TransientModel):
	_name = "wizard.member.list"

	status = fields.Selection([
		('all','Todos'),
		('active', 'Activo'),
		('holder', 'Tenedor'),
		('deceased', 'Fallecido'),
		#('discontinued', 'Suspendido'),
		('inactive', 'Inactivo'),
	], 'Estado', required=True,default='all')


	state_action = fields.Selection([
		('all', 'Todas'),
		('active', 'Activa'),
		('special', 'Especial'),
		('honorary', 'Honorario'),
		('treasury', 'Tesorería'),
	], 'Estado de la Acción',default='all',required=True)


	def print_pdf_member_list(self):
		print("PRINT")
		if not self.status:
			raise UserError("Estado es obligatorio")
		if not self.state_action:
			raise UserError("Estado de la Acción es obligatorio")

		data = {'form':{'status': self.status,'state_action': self.state_action}}
		return self.env.ref('country_socios_reportes.action_report_member_list').with_context(landscape=True).report_action(self, data=data)
