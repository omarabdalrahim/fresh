# -*- coding: utf-8 -*-
# from odoo import http


# class SalesReportCustom(http.Controller):
#     @http.route('/sales_report_custom/sales_report_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_report_custom/sales_report_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_report_custom.listing', {
#             'root': '/sales_report_custom/sales_report_custom',
#             'objects': http.request.env['sales_report_custom.sales_report_custom'].search([]),
#         })

#     @http.route('/sales_report_custom/sales_report_custom/objects/<model("sales_report_custom.sales_report_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_report_custom.object', {
#             'object': obj
#         })
