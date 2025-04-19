# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import RedirectWarning, UserError, ValidationError
import itertools
class salesorder(models.Model):
    _inherit = 'sale.order'
    meal_id = fields.Many2one("hr.meals")
class PRoduct(models.Model):
    _inherit = 'product.product'
    x_meals = fields.Boolean("IS Meal")
class Partner(models.Model):
    _inherit = 'res.partner'
    x_is_meals = fields.Boolean("عميل وجبات")
class meals(models.Model):
    _name = 'hr.meals'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'sequence.mixin']
    date = fields.Date(default=datetime.today())
    state = fields.Selection([('draft','Draft'),('confirm','Confirm')],default='draft')
    lines = fields.One2many("hr.meals.lines",'meal_id')
    name=fields.Char()

    employees = fields.Many2many(
        comodel_name='hr.employee',
        string='Employees')

    def action_confirm(self):
        self.state='confirm'
        for rec in self.lines:
            rec.state='confirm'
            rec.date=datetime.today()
        lines = self.env['hr.meals.lines']
        for rec in self.employees:
            lines.create({
                'employee_id':rec.id,
                'state':'confirm',
                'meal_id':self.id,
                'date':self.date

            })

    def unlink(self):
        res =super(meals, self).unlink()
        if res.state!='draft':
            raise  ValidationError("You Cann't Delete")
        return res



class Lines(models.Model):
    _name = 'hr.meals.lines'
    employee_id = fields.Many2one("hr.employee")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('out','Out')])
    date = fields.Date(default=datetime.today())
    product_id = fields.Many2one("product.product",domain="[('x_meals','=',True)]")
    meal_id = fields.Many2one("hr.meals")
    pin = fields.Char(related='employee_id.barcode',store=True,index=True)
    def unlink(self):
        res =super(Lines, self).unlink()
        if res.state!='draft':
            raise  ValidationError("You Cann't Delete")
        return res
    def action_out(self):
        lines = []

        partner_id = self.env['res.partner'].search([('x_is_meals','=',True)],limit=1)
        if not partner_id:
            raise ValidationError("please select Customer Meals")
        for rec in self:
            rec.state = 'out'
            if not rec.product_id:
                raise ValidationError("Please Check you add Product")
            lines.append({
                'product_id':rec.product_id,
                'id':int(rec.product_id.id),
                'name':str(rec.product_id.name),
                'product_uom_qty':1,
            })
        print(lines)
        out = sorted(lines, key=lambda i: (i['name']))
        docs = []
        for key, group in itertools.groupby(out, key=lambda x: (x['id'])):


            name=''
            total=0
            for item in group:
                total+=item['product_uom_qty']

                name = item['id']

            docs.append((0,0,{

                'product_id': name,
                'product_uom_qty': total
            }))
        sale_order = self.env['sale.order'].create({
            # 'meal_id':self.meal_id.id,
            'partner_id':partner_id.id,
            'order_line':docs
        })


