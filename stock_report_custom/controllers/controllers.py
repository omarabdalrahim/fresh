# -*- coding: utf-8 -*-
# from odoo import http


# class StockReportCustom(http.Controller):
#     @http.route('/stock_report_custom/stock_report_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_report_custom/stock_report_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_report_custom.listing', {
#             'root': '/stock_report_custom/stock_report_custom',
#             'objects': http.request.env['stock_report_custom.stock_report_custom'].search([]),
#         })

#     @http.route('/stock_report_custom/stock_report_custom/objects/<model("stock_report_custom.stock_report_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_report_custom.object', {
#             'object': obj
#         })
