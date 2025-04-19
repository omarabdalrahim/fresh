# -*- coding: utf-8 -*-
# from odoo import http


# class Meals(http.Controller):
#     @http.route('/meals/meals', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/meals/meals/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('meals.listing', {
#             'root': '/meals/meals',
#             'objects': http.request.env['meals.meals'].search([]),
#         })

#     @http.route('/meals/meals/objects/<model("meals.meals"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('meals.object', {
#             'object': obj
#         })
