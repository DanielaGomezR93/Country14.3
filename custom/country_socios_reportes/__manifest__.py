# -*- coding: utf-8 -*-
{
    'name': "country_socios_reportes",

    'summary': """
        Reportes para socios country""",

    'description': """
        Reportes para socios country
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','Country_Socios', 'binaural_anticipos'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        #'views/views.xml',
        #'views/templates.xml',
        'wizard/wizard_member_list.xml',
        'reports/member_list_report.xml',
        'wizard/advance_payment_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}