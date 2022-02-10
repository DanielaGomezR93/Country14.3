# -*- coding: utf-8 -*-

{
        'name': 'Country - Escanear Código Qr',
        'version': '1.9',
        'author': '[]',
        'website': '[]',
        'category': 'web',
        'description':
"""
Escanear código qr de socios para verificar solvencia

""",
        'depends': ['base', 'website', 'country_qr_code'],
        'data': [
        'security/scanner_security.xml',
        'views/res_groups_view.xml',
        'views/website_menu_view.xml',
        'views/views.xml',
        'views/add_js.xml',
	],
}

