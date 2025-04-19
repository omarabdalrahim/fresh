# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class PrdocutUrl(http.Controller):
    # @http.route('/prdocut_url/prdocut_url/', auth='public')
    # def index(self, **kw):
    #     return "Hello, world"
    #
    # @http.route('/prdocut_url/prdocut_url/objects/', auth='public')
    # def list(self, **kw):
    #     return http.request.render('prdocut_url.listing', {
    #         'root': '/prdocut_url/prdocut_url',
    #         'objects': http.request.env['prdocut_url.prdocut_url'].search([]),
    #     })

    @http.route('/pro/<int:id>', auth='public')
    def object(self, id, **kw):
        product_id = http.request.env['product.product'].sudo().search([('id','=',id)])

        return request.render('product.report_productlabel', {'docs': product_id})
        # return http.request.env.ref('product.report_productlabel').report_action(product_id)
        # return http.request.render('prdocut_url.object', {
        #     'object': obj
        # })
