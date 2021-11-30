# -*- coding: utf-8 -*-
from odoo import http

# class CountrySociosReportes(http.Controller):
#     @http.route('/country_socios_reportes/country_socios_reportes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/country_socios_reportes/country_socios_reportes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('country_socios_reportes.listing', {
#             'root': '/country_socios_reportes/country_socios_reportes',
#             'objects': http.request.env['country_socios_reportes.country_socios_reportes'].search([]),
#         })

#     @http.route('/country_socios_reportes/country_socios_reportes/objects/<model("country_socios_reportes.country_socios_reportes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('country_socios_reportes.object', {
#             'object': obj
#         })