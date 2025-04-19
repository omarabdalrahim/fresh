# -*- coding: utf-8 -*-
# from odoo import http


# class DanfershCustom(http.Controller):
#     @http.route('/danfersh_custom/danfersh_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/danfersh_custom/danfersh_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('danfersh_custom.listing', {
#             'root': '/danfersh_custom/danfersh_custom',
#             'objects': http.request.env['danfersh_custom.danfersh_custom'].search([]),
#         })

#     @http.route('/danfersh_custom/danfersh_custom/objects/<model("danfersh_custom.danfersh_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('danfersh_custom.object', {
#             'object': obj
#         })
