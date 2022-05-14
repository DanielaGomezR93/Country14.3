# -*- coding: utf-8 -*-
from odoo import api 
from odoo.addons.account_reports.models.account_cash_flow_report import AccountCashFlowReport

import logging
_logger = logging.getLogger(__name__)

@api.model
def _get_liquidity_move_ids(self, options):
    
    ''' Retrieve all liquidity moves to be part of the cash flow statement and also the accounts making them
    such moves.

    Adicionalmente se agrega un query para traerse los movimientos generados por las retenciones

    :param options: The report options.
    :return:        payment_move_ids: A tuple containing all account.move's ids being the liquidity moves.
                    payment_account_ids: A tuple containing all account.account's ids being used in a liquidity journal.
    '''
    new_options = self._get_options_current_period(options)
    selected_journals = self._get_options_journals(options)

    # Fetch liquidity accounts:
    # Accounts being used by at least one bank / cash journal.
    selected_journal_ids = [j['id'] for j in selected_journals]
    if selected_journal_ids:
        where_clause = "account_journal.id IN %s"
        where_params = [tuple(selected_journal_ids)]
    else:
        where_clause = "account_journal.type IN ('bank', 'cash')"
        where_params = []

    query = '''
        SELECT ARRAY_AGG(DISTINCT default_account_id),
            ARRAY_AGG(DISTINCT payment_debit_account_id),
            ARRAY_AGG(DISTINCT payment_credit_account_id)
        FROM account_journal
        WHERE ''' + where_clause
    
    self._cr.execute(query, where_params)
    res = self._cr.fetchall()[0]
    
    payment_account_ids = set((res[0] or []) + (res[1] or []) + (res[2] or []))            

    if not payment_account_ids:
        return (), ()

    # Fetch journal entries:
    # account.move having at least one line using a liquidity account.
    payment_move_ids = set()
    tables, where_clause, where_params = self._query_get(new_options, [('account_id', 'in', list(payment_account_ids))])

    query = '''
        SELECT DISTINCT account_move_line.move_id
        FROM ''' + tables + '''
        WHERE ''' + where_clause + '''
        GROUP BY account_move_line.move_id
    '''
    
    self._cr.execute(query, where_params)
    for res in self._cr.fetchall():        
        payment_move_ids.add(res[0])        

    _logger.info("Edicion de flujo de efectivo para incluir retenciones")
    #TODO: esta solucion solo aplica para las retenciones donde el prefijo es RIV
    # cuando se haga el cambio a retenciones como pagos de odoo esto ya no sera necesario
    query_add = '''
        SELECT DISTINCT aml.move_id 
        from account_move_line as aml
        left join account_move as am on aml.move_id = am.id
        where (aml.display_type not in ('line_section','line_note') or (aml.display_type is NULL))
        and (aml.move_name like 'RIV-%')
        order by move_id
    '''
    self._cr.execute(query_add)
    for res_add in self._cr.fetchall():
        payment_move_ids.add(res_add[0])
    # Fin codigo nuevo para flujo de efectivo country
        
    return tuple(payment_move_ids), tuple(payment_account_ids)

AccountCashFlowReport._get_liquidity_move_ids = _get_liquidity_move_ids