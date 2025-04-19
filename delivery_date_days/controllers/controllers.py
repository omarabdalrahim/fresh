# -*- coding: utf-8 -*-
# from odoo import http


# class DeliveryDateDays(http.Controller):
#     @http.route('/delivery_date_days/delivery_date_days', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/delivery_date_days/delivery_date_days/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('delivery_date_days.listing', {
#             'root': '/delivery_date_days/delivery_date_days',
#             'objects': http.request.env['delivery_date_days.delivery_date_days'].search([]),
#         })

#     @http.route('/delivery_date_days/delivery_date_days/objects/<model("delivery_date_days.delivery_date_days"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('delivery_date_days.object', {
#             'object': obj
#         })
