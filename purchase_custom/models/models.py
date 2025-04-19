# -*- coding: utf-8 -*-

from odoo import models, fields, api


class purchase_custom(models.Model):
    _inherit = 'purchase.order.line'
    increment = fields.Float("زياده")

    @api.onchange('increment')
    def onchnage_increment(self):
        if self.increment:
            self.product_qty+=(self.product_qty*(self.increment/100))
#     _name = 'purchase_custom.purchase_custom'
#     _description = 'purchase_custom.purchase_custom'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
