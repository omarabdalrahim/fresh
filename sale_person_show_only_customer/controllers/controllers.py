# -*- coding: utf-8 -*-
# from odoo import http


# class SalePersonShowOnlyCustomer(http.Controller):
#     @http.route('/sale_person_show_only_customer/sale_person_show_only_customer', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_person_show_only_customer/sale_person_show_only_customer/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_person_show_only_customer.listing', {
#             'root': '/sale_person_show_only_customer/sale_person_show_only_customer',
#             'objects': http.request.env['sale_person_show_only_customer.sale_person_show_only_customer'].search([]),
#         })

#     @http.route('/sale_person_show_only_customer/sale_person_show_only_customer/objects/<model("sale_person_show_only_customer.sale_person_show_only_customer"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_person_show_only_customer.object', {
#             'object': obj
#         })
