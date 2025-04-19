# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class prepared_product_so(models.Model):
#     _name = 'prepared_product_so.prepared_product_so'
#     _description = 'prepared_product_so.prepared_product_so'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
