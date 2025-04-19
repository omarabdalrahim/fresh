# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Fleet(models.Model):
    _inherit = "fleet.vehicle.log.services"
    expense_id = fields.Many2one("hr.expense")

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for rec in self:
            if rec.expense_id:
                rec.expense_id.is_service = True
        return res


class expense_partner(models.Model):
    _inherit = "hr.expense"
    is_service = fields.Boolean()
    count_service = fields.Integer(compute='get_count_service')

    def action_submit_expenses(self):
        if self.x_fleet_id and self.count_service==0:
            return self.crate_service()

        return super().action_submit_expenses()

    def get_count_service(self):
        for rec in self:
            rec.count_service = 0
            if rec.id:
                if self.env['fleet.vehicle.log.services'].sudo().search([('expense_id', '=', rec.id)]):
                    rec.count_service = len(
                        self.env['fleet.vehicle.log.services'].sudo().search([('expense_id', '=', rec.id)]))

    def crate_service(self):
        return {
            'name': ('Service'),
            'view_mode': 'form',
            'view_id': self.env.ref('expense_partner.vehicle_inherited').id,
            'res_model': 'fleet.vehicle.log.services',
            'context': {'default_expense_id': self.id, 'default_amount': self.total_amount,
                        'default_vehicle_id': self.x_fleet_id.id},
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def view_service(self):
        return {
            'name': ('Service'),
            'view_mode': 'tree,form',

            'res_model': 'fleet.vehicle.log.services',
            'domain': [('expense_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'create': False},
            'target': 'current'
        }
