# -*- coding: utf-8 -*-
{
    'name': "Country_Anticipo_Proveedores/Clientes",

    'summary': """
        Country Anticipo Proveedores/Clientes
       """,

    'description': """
        Binaural Anticipo Proveedores/Clientes
    """,

    'author': "Binaural",
    'website': "https://binauraldev.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['binaural_anticipos', 'Country_Socios'],

    # always loaded
    'data': [
        'reports/report_advance_payment_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}