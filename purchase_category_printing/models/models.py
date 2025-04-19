# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase(models.Model):
    _inherit = 'purchase.order'
    discount_print = fields.Float("Discount Printing")
    create_dt = fields.Date("CREATE DATE",compute="get_date")

    @api.depends("create_date")
    def get_date(self):
        for rec in self:
            rec.create_dt = rec.create_date.date()
# class PersonPurchas(models.Model):
#     _inherit = 'x_purchase.person.lines'
#     create_dt = fields.Date("FFf",compute="get_date")
#
#     @api.depends("x_date")
#     def get_date(self):
#         for rec in self:
#             rec.create_dt = rec.x_date.date()


# class purchase_category_printing(models.Model):
#     _name = 'purchase_category_printing.purchase_category_printing'
#     _description = 'purchase_category_printing.purchase_category_printing'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
