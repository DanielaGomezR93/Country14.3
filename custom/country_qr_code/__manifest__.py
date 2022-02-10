# -*- coding: utf-8 -*-
{
    'name': "Codigo Qr para Socios",

    'summary': """
        Genera un codigo Qr para los socios""",

    'description': """
         Este modulo esta pensando para los socios del country
    """,

    'author': "Antony H.",
    'company': 'Binauraldev',
    'maintainer': 'Antony H. / Binauraldev',
    'website': "https://www.binauraldev.com",
    'category': 'Tools',
    'version': '12.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'event'],

    # always loaded
    'data': [
        'report/paperformat.xml',
        'report/report.xml',
        'views/res_partner.xml',
        'report/template.xml',
    ],
    'demo': [],
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}