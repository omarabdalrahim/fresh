# -*- coding: utf-8 -*-
# from odoo import http


# class CreditNoteSalesOrder(http.Controller):
#     @http.route('/credit_note_sales_order/credit_note_sales_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/credit_note_sales_order/credit_note_sales_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('credit_note_sales_order.listing', {
#             'root': '/credit_note_sales_order/credit_note_sales_order',
#             'objects': http.request.env['credit_note_sales_order.credit_note_sales_order'].search([]),
#         })

#     @http.route('/credit_note_sales_order/credit_note_sales_order/objects/<model("credit_note_sales_order.credit_note_sales_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('credit_note_sales_order.object', {
#             'object': obj
#         })
