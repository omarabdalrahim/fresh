# -*- coding: utf-8 -*-
# from odoo import http


# class InternalSaleOrder(http.Controller):
#     @http.route('/internal_sale_order/internal_sale_order/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/internal_sale_order/internal_sale_order/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('internal_sale_order.listing', {
#             'root': '/internal_sale_order/internal_sale_order',
#             'objects': http.request.env['internal_sale_order.internal_sale_order'].search([]),
#         })

#     @http.route('/internal_sale_order/internal_sale_order/objects/<model("internal_sale_order.internal_sale_order"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('internal_sale_order.object', {
#             'object': obj
#         })
