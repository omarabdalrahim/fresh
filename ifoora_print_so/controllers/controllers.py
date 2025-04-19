# -*- coding: utf-8 -*-
# from odoo import http


# class IfooraPrintSo(http.Controller):
#     @http.route('/ifoora_print_so/ifoora_print_so', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ifoora_print_so/ifoora_print_so/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('ifoora_print_so.listing', {
#             'root': '/ifoora_print_so/ifoora_print_so',
#             'objects': http.request.env['ifoora_print_so.ifoora_print_so'].search([]),
#         })

#     @http.route('/ifoora_print_so/ifoora_print_so/objects/<model("ifoora_print_so.ifoora_print_so"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ifoora_print_so.object', {
#             'object': obj
#         })
