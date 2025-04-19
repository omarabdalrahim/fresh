# -*- coding: utf-8 -*-
# from odoo import http


# class ResPartnerPosMerge(http.Controller):
#     @http.route('/res_partner_pos_merge/res_partner_pos_merge/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/res_partner_pos_merge/res_partner_pos_merge/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('res_partner_pos_merge.listing', {
#             'root': '/res_partner_pos_merge/res_partner_pos_merge',
#             'objects': http.request.env['res_partner_pos_merge.res_partner_pos_merge'].search([]),
#         })

#     @http.route('/res_partner_pos_merge/res_partner_pos_merge/objects/<model("res_partner_pos_merge.res_partner_pos_merge"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('res_partner_pos_merge.object', {
#             'object': obj
#         })
