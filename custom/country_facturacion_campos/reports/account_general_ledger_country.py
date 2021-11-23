# -*- coding: utf-8 -*-

from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountReportGeneralLedgerCountry(models.TransientModel):
    _inherit = "account.common.account.report"
    _name = "account.report.general.ledger.country"
    _description = "General Ledger Report Country Club"

    initial_balance = fields.Boolean(string='Incluir Balance Inicial',
                                    help='If you selected date, this field allow you to add a row to display the amount of debit/credit/balance that precedes the filter you\'ve set.')
    sortby = fields.Selection([('sort_date', 'Fecha'), ('sort_journal_partner', 'Diario y Contacto')], string='Ordenar por', required=True, default='sort_date')
    journal_ids = fields.Many2many('account.journal', 'account_report_general_ledger_journal_rel_country', 'account_id', 'journal_id', string='Diarios', required=True)
    account_ids_country = fields.Many2many('account.account', string='Cuentas Contables')
    display_account = fields.Selection([('all', 'Todas'), ('movement', 'Con movimientos'),
                                        ('not_zero', 'Con saldo no es igual a 0'), ],
                                       string='Mostrar cuentas', required=True, default='movement')
    target_move = fields.Selection([('posted', 'Todos los asientos publicados'),
                                    ('all', 'Todos los asientos'),
                                    ], string='Movimientos', required=True, default='posted')
    date_from = fields.Date(string='Fecha Inicial')
    date_to = fields.Date(string='Fecha Final')
    another_currency = fields.Boolean(string='En Bolivares')
    
    def _print_report(self, data):
        data = self.pre_print_report(data)
        data['form'].update(self.read(['initial_balance', 'sortby'])[0])

        data['form'].update(self.read(['account_ids_country'])[0])

        if data['form'].get('initial_balance') and not data['form'].get('date_from'):
            raise UserError(_("You must define a Start Date"))
        records = self.env[data['model']].browse(data.get('ids', []))
        data['form'].update(self.read(['another_currency'])[0])
        return self.env.ref('country_facturacion_campos.action_report_general_ledger_country').with_context(landscape=False).report_action(records, data=data)
