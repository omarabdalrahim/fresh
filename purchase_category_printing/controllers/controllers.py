# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseCategoryPrinting(http.Controller):
#     @http.route('/purchase_category_printing/purchase_category_printing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_category_printing/purchase_category_printing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_category_printing.listing', {
#             'root': '/purchase_category_printing/purchase_category_printing',
#             'objects': http.request.env['purchase_category_printing.purchase_category_printing'].search([]),
#         })

#     @http.route('/purchase_category_printing/purchase_category_printing/objects/<model("purchase_category_printing.purchase_category_printing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_category_printing.object', {
#             'object': obj
#         })
