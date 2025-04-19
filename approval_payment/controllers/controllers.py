# -*- coding: utf-8 -*-
# from odoo import http


# class ApprovalPayment(http.Controller):
#     @http.route('/approval_payment/approval_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/approval_payment/approval_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('approval_payment.listing', {
#             'root': '/approval_payment/approval_payment',
#             'objects': http.request.env['approval_payment.approval_payment'].search([]),
#         })

#     @http.route('/approval_payment/approval_payment/objects/<model("approval_payment.approval_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('approval_payment.object', {
#             'object': obj
#         })
