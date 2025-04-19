# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WeekDays(models.Model):
    _name='week.days'

    name=fields.Char('Day')
    code=fields.Integer('Code')

class Partner(models.Model):
    _inherit = 'res.partner'

    delivery_days = fields.Many2many('week.days')

class Sale(models.Model):
    _inherit = 'sale.order'
    # delivery_date= fields.Date('Delivery Date')
    delivery_comment= fields.Text('Delivery Comment')
    @api.model
    def create(self,vals):

        res = super(Sale, self).create(vals)
        if self.env.user.has_group('Sales.group_sales_person_mandob'):
            raise ValidationError("you cann't create order")


        if res.partner_id.state_id:
            if res.partner_id.state_id.x_warehouse_id:
                res.warehouse_id = res.partner_id.state_id.x_warehouse_id.id
        return res
