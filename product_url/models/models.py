# -*- coding: utf-8 -*-

from odoo import models, fields, api


class prdocut_url(models.Model):
    _inherit = 'sale.order.line'
    product_url = fields.Char(compute='get_product_url')
    @api.depends('product_id')
    def get_product_url(self):
        for rec in self:
            rec.product_url=''
            if rec.product_id:
                rec.product_url = 'https://silvergroup.odoo.com/pro/'+str(rec.product_id.id)

    def print_label(self,product_id):
        action=self.env.ref('product.report_product_label').report_action(product_id)
        print(">>><<<<<<<action",action)
        return action
#     _name = 'prdocut_url.prdocut_url'
#     _description = 'prdocut_url.prdocut_url'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
