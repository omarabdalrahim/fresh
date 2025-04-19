# -*- coding: utf-8 -*-
# from odoo import http


# class ExpensePartner(http.Controller):
#     @http.route('/expense_partner/expense_partner', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/expense_partner/expense_partner/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('expense_partner.listing', {
#             'root': '/expense_partner/expense_partner',
#             'objects': http.request.env['expense_partner.expense_partner'].search([]),
#         })

#     @http.route('/expense_partner/expense_partner/objects/<model("expense_partner.expense_partner"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('expense_partner.object', {
#             'object': obj
#         })
