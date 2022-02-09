--type resultado
-- CREATE TYPE table_result as (code character varying(64), init_balance NUMERIC, credit NUMERIC, debit NUMERIC, balance NUMERIC);

drop FUNCTION all_accounts_balance;
-- funcion
CREATE OR REPLACE FUNCTION all_accounts_balance (date_from date, date_until date, journal_list int[], company_id_param int)
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

    select id, name, code, root_id from account_account order by code;

    
    return;
end;
$$
