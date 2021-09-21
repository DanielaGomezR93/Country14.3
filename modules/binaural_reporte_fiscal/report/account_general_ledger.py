
from odoo import models, fields, api, _
from odoo.tools.misc import format_date, DEFAULT_SERVER_DATE_FORMAT
from datetime import timedelta
from pprint import pprint


class AccountGeneralLedgerReportBinaural(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def _get_query_sums(self, options_list, expanded_account=None):
        ''' Construct a query retrieving all the aggregated sums to build the report. It includes:
        - sums for all accounts.
        - sums for the initial balances.
        - sums for the unaffected earnings.
        - sums for the tax declaration.
        :param options_list:        The report options list, first one being the current dates range, others being the
                                    comparisons.
        :param expanded_account:    An optional account.account record that must be specified when expanding a line
                                    with of without the load more.
        :return:                    (query, params)
        '''
        options = options_list[0]
        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        params = []
        queries = []

        # Create the currency table.
        # As the currency table is the same whatever the comparisons, create it only once.
        ct_query = self.env['res.currency']._get_query_currency_table(options)

        # ============================================
        # 1) Get sums for all accounts.
        # ============================================

        domain = [('account_id', '=', expanded_account.id)] if expanded_account else []

        currency_id = self.get_option_currency(options['currency'])
        if currency_id != self.env.user.company_id.currency_id.id:
            flag = True
        else:
            flag = False

        for i, options_period in enumerate(options_list):
            # The period domain is expressed as:
            # [
            #   ('date' <= options['date_to']),
            #   '|',
            #   ('date' >= fiscalyear['date_from']),
            #   ('account_id.user_type_id.include_initial_balance', '=', True),
            # ]

            new_options = self._get_options_sum_balance(options_period)
            tables, where_clause, where_params = self._query_get(new_options, domain=domain)
            params += where_params

            if flag:
                queries.append('''
                        SELECT
                            account_move_line.account_id                            AS groupby,
                            'sum'                                                   AS key,
                            MAX(account_move_line.date)                             AS max_date,
                            %s                                                      AS period_number,
                            COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                            SUM(ROUND(account_move_line.debit * account_move_line.foreign_currency_rate, currency_table.precision))   AS debit,
                            SUM(ROUND(account_move_line.credit * account_move_line.foreign_currency_rate, currency_table.precision))  AS credit,
                            SUM(ROUND(account_move_line.balance * account_move_line.foreign_currency_rate, currency_table.precision)) AS balance
                        FROM %s
                        LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                        WHERE %s
                        GROUP BY account_move_line.account_id
                    ''' % (i, tables, ct_query, where_clause))
            else:
                queries.append('''
                                    SELECT
                                        account_move_line.account_id                            AS groupby,
                                        'sum'                                                   AS key,
                                        MAX(account_move_line.date)                             AS max_date,
                                        %s                                                      AS period_number,
                                        COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                                        SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                                        SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                                        SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                                    FROM %s
                                    LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                                    WHERE %s
                                    GROUP BY account_move_line.account_id
                                ''' % (i, tables, ct_query, where_clause))
        # ============================================
        # 2) Get sums for the unaffected earnings.
        # ============================================

        domain = [('account_id.user_type_id.include_initial_balance', '=', False)]
        if expanded_account:
            domain.append(('company_id', '=', expanded_account.company_id.id))

        # Compute only the unaffected earnings for the oldest period.

        i = len(options_list) - 1
        options_period = options_list[-1]

        # The period domain is expressed as:
        # [
        #   ('date' <= fiscalyear['date_from'] - 1),
        #   ('account_id.user_type_id.include_initial_balance', '=', False),
        # ]

        new_options = self._get_options_unaffected_earnings(options_period)
        tables, where_clause, where_params = self._query_get(new_options, domain=domain)
        params += where_params

        if flag:
            queries.append('''
                    SELECT
                        account_move_line.company_id                            AS groupby,
                        'unaffected_earnings'                                   AS key,
                        NULL                                                    AS max_date,
                        %s                                                      AS period_number,
                        COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                        SUM(ROUND(account_move_line.debit * account_move_line.foreign_currency_rate, currency_table.precision))   AS debit,
                        SUM(ROUND(account_move_line.credit * account_move_line.foreign_currency_rate, currency_table.precision))  AS credit,
                        SUM(ROUND(account_move_line.balance * account_move_line.foreign_currency_rate, currency_table.precision)) AS balance
                    FROM %s
                    LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                    WHERE %s
                    GROUP BY account_move_line.company_id
                ''' % (i, tables, ct_query, where_clause))
        else:
            queries.append('''
                                SELECT
                                    account_move_line.company_id                            AS groupby,
                                    'unaffected_earnings'                                   AS key,
                                    NULL                                                    AS max_date,
                                    %s                                                      AS period_number,
                                    COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                                    SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                                    SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                                FROM %s
                                LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                                WHERE %s
                                GROUP BY account_move_line.company_id
                            ''' % (i, tables, ct_query, where_clause))

        # ============================================
        # 3) Get sums for the initial balance.
        # ============================================

        domain = None
        if expanded_account:
            domain = [('account_id', '=', expanded_account.id)]
        elif unfold_all:
            domain = []
        elif options['unfolded_lines']:
            domain = [('account_id', 'in', [int(line[8:]) for line in options['unfolded_lines']])]

        if domain is not None:
            for i, options_period in enumerate(options_list):
                # The period domain is expressed as:
                # [
                #   ('date' <= options['date_from'] - 1),
                #   '|',
                #   ('date' >= fiscalyear['date_from']),
                #   ('account_id.user_type_id.include_initial_balance', '=', True)
                # ]

                new_options = self._get_options_initial_balance(options_period)
                tables, where_clause, where_params = self._query_get(new_options, domain=domain)
                params += where_params
                if flag:
                    queries.append('''
                            SELECT
                                account_move_line.account_id                            AS groupby,
                                'initial_balance'                                       AS key,
                                NULL                                                    AS max_date,
                                %s                                                      AS period_number,
                                COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                                SUM(ROUND(account_move_line.debit * account_move_line.foreign_currency_rate, currency_table.precision))   AS debit,
                                SUM(ROUND(account_move_line.credit * account_move_line.foreign_currency_rate, currency_table.precision))  AS credit,
                                SUM(ROUND(account_move_line.balance * account_move_line.foreign_currency_rate, currency_table.precision)) AS balance
                            FROM %s
                            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                            WHERE %s
                            GROUP BY account_move_line.account_id
                        ''' % (i, tables, ct_query, where_clause))
                else:
                    queries.append('''
                                    SELECT
                                        account_move_line.account_id                            AS groupby,
                                        'initial_balance'                                       AS key,
                                        NULL                                                    AS max_date,
                                        %s                                                      AS period_number,
                                        COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                                        SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                                        SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                                        SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                                    FROM %s
                                    LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                                    WHERE %s
                                    GROUP BY account_move_line.account_id
                                ''' % (i, tables, ct_query, where_clause))

        # ============================================
        # 4) Get sums for the tax declaration.
        # ============================================

        journal_options = self._get_options_journals(options)
        if not expanded_account and len(journal_options) == 1 and journal_options[0]['type'] in ('sale', 'purchase'):
            for i, options_period in enumerate(options_list):
                tables, where_clause, where_params = self._query_get(options_period)
                params += where_params + where_params

                if flag:
                    queries += ['''
                            SELECT
                                tax_rel.account_tax_id                  AS groupby,
                                'base_amount'                           AS key,
                                NULL                                    AS max_date,
                                %s                                      AS period_number,
                                0.0                                     AS amount_currency,
                                0.0                                     AS debit,
                                0.0                                     AS credit,
                                SUM(ROUND(account_move_line.balance * account_move_line.foreign_currency_rate, currency_table.precision)) AS balance
                            FROM account_move_line_account_tax_rel tax_rel, %s
                            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                            WHERE account_move_line.id = tax_rel.account_move_line_id AND %s
                            GROUP BY tax_rel.account_tax_id
                        ''' % (i, tables, ct_query, where_clause), '''
                            SELECT
                            account_move_line.tax_line_id               AS groupby,
                            'tax_amount'                                AS key,
                                NULL                                    AS max_date,
                                %s                                      AS period_number,
                                0.0                                     AS amount_currency,
                                0.0                                     AS debit,
                                0.0                                     AS credit,
                                SUM(ROUND(account_move_line.balance * account_move_line.foreign_currency_rate, currency_table.precision)) AS balance
                            FROM %s
                            LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                            WHERE %s
                            GROUP BY account_move_line.tax_line_id
                        ''' % (i, tables, ct_query, where_clause)]
                else:
                    queries += ['''
                                SELECT
                                    tax_rel.account_tax_id                  AS groupby,
                                    'base_amount'                           AS key,
                                    NULL                                    AS max_date,
                                    %s                                      AS period_number,
                                    0.0                                     AS amount_currency,
                                    0.0                                     AS debit,
                                    0.0                                     AS credit,
                                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                                FROM account_move_line_account_tax_rel tax_rel, %s
                                LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                                WHERE account_move_line.id = tax_rel.account_move_line_id AND %s
                                GROUP BY tax_rel.account_tax_id
                            ''' % (i, tables, ct_query, where_clause), '''
                                SELECT
                                account_move_line.tax_line_id               AS groupby,
                                'tax_amount'                                AS key,
                                    NULL                                    AS max_date,
                                    %s                                      AS period_number,
                                    0.0                                     AS amount_currency,
                                    0.0                                     AS debit,
                                    0.0                                     AS credit,
                                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance
                                FROM %s
                                LEFT JOIN %s ON currency_table.company_id = account_move_line.company_id
                                WHERE %s
                                GROUP BY account_move_line.tax_line_id
                            ''' % (i, tables, ct_query, where_clause)]

        return ' UNION ALL '.join(queries), params

    def get_option_currency(self, option_currency):
        for currency in option_currency:
            if currency.get('selected'):
                return currency.get('id')