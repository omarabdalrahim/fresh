# -*- coding: utf-8 -*-
# from odoo import http


# class ReturnFromSalesOrder(http.Controller):
#     @http.route('/return_from_sales_order/return_from_sales_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/return_from_sales_order/return_from_sales_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('return_from_sales_order.listing', {
#             'root': '/return_from_sales_order/return_from_sales_order',
#             'objects': http.request.env['return_from_sales_order.return_from_sales_order'].search([]),
#         })

#     @http.route('/return_from_sales_order/return_from_sales_order/objects/<model("return_from_sales_order.return_from_sales_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('return_from_sales_order.object', {
#             'object': obj
#         })
