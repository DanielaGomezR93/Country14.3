--type resultado
-- CREATE TYPE table_result as (code character varying(64), init_balance NUMERIC, credit NUMERIC, debit NUMERIC, balance NUMERIC);

drop FUNCTION merge_init_filtered_balance;
-- funcion
CREATE OR REPLACE FUNCTION merge_init_filtered_balance (date_from date, date_until date, journal_list int[], company_id_param int)
returns setof table_result  
   language plpgsql
  as
$$
declare 
-- variable declaration
parent_state_posted character varying(50);
parent_state_cancel character varying(50);
var_display_type CHARACTER varying(50)[];
count_filtered_balance int;
count_initial_balance int;
cursor_balance refcursor;
cursor_row record;
balance_row_by_code record;

begin

    parent_state_posted := 'posted';
    parent_state_cancel := 'cancel';
    var_display_type := ARRAY['line_section','line_note'];

    -- obtener cantidad de registros de consulta de balance
    with filtered_balance as (
        SELECT aml.account_id AS id, aa.code as code, SUM(aml.debit) AS debit, SUM(aml.credit) AS credit, (SUM(aml.debit) - SUM(aml.credit)) AS balance
        FROM account_move_line AS aml 
            inner join account_account as aa on aml.account_id = aa.id
        WHERE 	
            (((((((aml.date <= date_until) 
                    AND (aml.date >= date_from)) 
                    AND (aml.journal_id = any(journal_list))) 
                    AND (aml.parent_state = parent_state_posted)) 
                AND (aml.company_id = company_id_param)) 
                AND ((aml.display_type not in ('line_section','line_note')) OR aml.display_type IS NULL)) 
                AND ((aml.parent_state != parent_state_cancel) OR aml.parent_state IS NULL)) 
                AND (aml.company_id IS NULL  OR (aml.company_id in (company_id_param))) 	
                GROUP BY aml.account_id, aa.code
                order by aa.code
    )

    select count(*) into count_filtered_balance from filtered_balance;

    -- obtener cantidad de registros de consulta de saldo inicial
    with initial_balance as(
        SELECT aml.account_id AS id, aa.code as code, (SUM(aml.debit) - SUM(aml.credit)) AS init_balance 
            FROM account_move as am
                INNER JOIN account_move_line as aml on am.id = aml.move_id
                INNER JOIN account_account  as aa on aml.account_id = aa.id
        WHERE 		
            aml.journal_id = any(journal_list) 
            AND am.date < date_from 
            AND am.state = parent_state_posted
        GROUP BY aml.account_id, aa.code
        order by aa.code
    )

    select count(*) into count_initial_balance from initial_balance;

    RAISE NOTICE USING MESSAGE = 'filtrado: ' || count_filtered_balance;
    RAISE NOTICE USING MESSAGE = 'inicial: ' || count_initial_balance;

    IF count_filtered_balance <= count_initial_balance THEN
        RAISE NOTICE USING MESSAGE = 'filtrado mayor o igual';
        open cursor_balance for execute 'SELECT aml.account_id AS id, aa.code as code, (SUM(aml.debit) - SUM(aml.credit)) AS init_balance 
            FROM account_move as am
                INNER JOIN account_move_line as aml on am.id = aml.move_id
                INNER JOIN account_account  as aa on aml.account_id = aa.id
        WHERE 		
            aml.journal_id in (' || array_to_string(journal_list,',') || ') 
            AND am.date < ''' || date_from || 
            ''' AND am.state = ''' || parent_state_posted || ''' GROUP BY aml.account_id, aa.code
        order by aa.code';	

        loop
            fetch next from cursor_balance into cursor_row;
            exit when cursor_row is null;
            
            SELECT aml.account_id AS id, aa.code as code, SUM(aml.debit) AS debit, SUM(aml.credit) AS credit, (SUM(aml.debit) - SUM(aml.credit)) AS balance
            FROM account_move_line AS aml 
            inner join account_account as aa on aml.account_id = aa.id
            WHERE 	
            (((((((aml.date <= date_until) 
                    AND (aml.date >= date_from)) 
                    AND (aml.journal_id = any(journal_list))) 
                    AND (aml.parent_state = parent_state_posted)) 
                AND (aml.company_id = company_id_param)) 
                AND ((aml.display_type not in ('line_section','line_note')) OR aml.display_type IS NULL)) 
                AND ((aml.parent_state != parent_state_cancel) OR aml.parent_state IS NULL)) 
                AND (aml.company_id IS NULL  OR (aml.company_id in (company_id_param))) 
                AND aa.code = cursor_row.code	
                GROUP BY aml.account_id, aa.code
                order by aa.code into balance_row_by_code; 

            if balance_row_by_code.code is not NULL THEN
				return query
                select * from (values (cursor_row.code, 
									   cursor_row.init_balance, 
                                       balance_row_by_code.debit,
									   balance_row_by_code.credit,									   
									   cursor_row.init_balance + (balance_row_by_code.debit - balance_row_by_code.credit))) t;
                -- return next t;                
            else
				return query
                select * from (values (cursor_row.code,
									  cursor_row.init_balance,
									  0::NUMERIC,
									  0::NUMERIC,
									  cursor_row.init_balance)) t;
                -- return next t;
            end if;

        end loop;
    else
        RAISE NOTICE USING MESSAGE = 'inicial mayor';
        open cursor_balance for execute 
        'SELECT aml.account_id AS id, aa.code as code, SUM(aml.debit) AS debit, SUM(aml.credit) AS credit, (SUM(aml.debit) - SUM(aml.credit)) AS balance
        FROM account_move_line AS aml 
            inner join account_account as aa on aml.account_id = aa.id
        WHERE 	
            ((((((aml.date <= ''' || date_until || ''') 
                    AND (aml.date >= ''' || date_from || ''')) 
                    AND (aml.journal_id in (' || array_to_string(journal_list,',') || '))) 
                    AND (aml.parent_state = ''' || parent_state_posted || ''')) 
                AND (aml.company_id = ' || company_id_param || ')) 
                AND ((aml.display_type not in (''line_section'',''line_note'') OR aml.display_type IS NULL)) 
                AND ((aml.parent_state != ''' || parent_state_cancel || ''') OR aml.parent_state IS NULL)) 
                AND (aml.company_id IS NULL  OR (aml.company_id in (' || company_id_param || '))) 	
                GROUP BY aml.account_id, aa.code
                order by aa.code';

        loop
            fetch next from cursor_balance into cursor_row;
            exit when cursor_row is null;

            SELECT aml.account_id AS id, aa.code as code, (SUM(aml.debit) - SUM(aml.credit)) AS init_balance 
            FROM account_move as am
                INNER JOIN account_move_line as aml on am.id = aml.move_id
                INNER JOIN account_account  as aa on aml.account_id = aa.id
            WHERE 		
            aml.journal_id = any(journal_list) 
            AND am.date < date_from 
            AND am.state = parent_state_posted
            AND aa.code = cursor_row.code
            GROUP BY aml.account_id, aa.code
            order by aa.code into balance_row_by_code;

            if balance_row_by_code.code is not NULL THEN   
                RAISE NOTICE USING MESSAGE = 'si filtrado esta en inicial';             
                return query
                select * from (values (cursor_row.code,
                    balance_row_by_code.init_balance,
                    cursor_row.debit,
                    cursor_row.credit,
                    balance_row_by_code.init_balance + (cursor_row.debit - cursor_row.credit))) t;
                -- return next t;                
            else           
                RAISE NOTICE USING MESSAGE = 'si filtrado NO esta en inicial';     
                return query
                select * from (values (
                    cursor_row.code,
                    0::NUMERIC,
                    cursor_row.debit,
                    cursor_row.credit,                    
                    cursor_row.debit - cursor_row.credit
                )) t;
                -- return next t;                
            end if;
        end loop;
    END IF;

    return;
end;
$$
