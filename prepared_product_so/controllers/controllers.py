# -*- coding: utf-8 -*-
# from odoo import http


# class PreparedProductSo(http.Controller):
#     @http.route('/prepared_product_so/prepared_product_so/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/prepared_product_so/prepared_product_so/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('prepared_product_so.listing', {
#             'root': '/prepared_product_so/prepared_product_so',
#             'objects': http.request.env['prepared_product_so.prepared_product_so'].search([]),
#         })

#     @http.route('/prepared_product_so/prepared_product_so/objects/<model("prepared_product_so.prepared_product_so"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('prepared_product_so.object', {
#             'object': obj
#         })
