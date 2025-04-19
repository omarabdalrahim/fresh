# -*- coding: utf-8 -*-

from odoo import models, fields, api

# x_approve_id
class Payment(models.Model):
    _inherit  = 'account.payment'
    x_approve_id =fields.Many2one('approval.request')

class approval_payment(models.Model):
    _inherit =  'approval.request'
    payment_count = fields.Float(compute='get_payment_count')

    @api.depends('name')
    def get_payment_count(self):
        for rec in self:
            rec.payment_count=0
            if rec.id:

                payment_id = self.env['account.payment'].search([('x_approve_id','=',rec.id)])
                if payment_id:
                    rec.payment_count=len(payment_id)



    def create_payment(self):
        return {
            'name': ('Payment'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'account.payment',
            'context':{'default_x_approve_id':self.id,'default_amount':self.amount},
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    def action_view_payment(self):

        return {
            'name': ('Payment'),
            'view_mode': 'tree,form',


            'res_model': 'account.payment',
            'domain':[('x_approve_id','=',self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }