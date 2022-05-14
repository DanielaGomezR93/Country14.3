# -*- coding: utf-8 -*-
# from odoo import http


# class CountryReportes(http.Controller):
#     @http.route('/country_reportes/country_reportes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/country_reportes/country_reportes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('country_reportes.listing', {
#             'root': '/country_reportes/country_reportes',
#             'objects': http.request.env['country_reportes.country_reportes'].search([]),
#         })

#     @http.route('/country_reportes/country_reportes/objects/<model("country_reportes.country_reportes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('country_reportes.object', {
#             'object': obj
#         })
