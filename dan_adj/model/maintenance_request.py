from odoo import fields, models, api

import itertools
class Maintenance(models.Model):
    _inherit = 'maintenance.request'

    alert_id = fields.Many2one('quality.alert', string='Alert Reference')
    @api.model
    def create(self,vals):
        res = super(Maintenance,self).create(vals)
        if res.alert_id:
            res.alert_id.maintenance_ids+=res
        return res

class Alert(models.Model):
    _inherit='quality.alert'

    maintenance_count = fields.Integer(compute='get_main_count')
    maintenance_ids = fields.Many2many('maintenance.request')

    def get_main_count(self):
        for i in self:
            i.maintenance_count=len(i.maintenance_ids)


    def return_main_ids(self):
        return ({
            'name': 'Maintenance Request',
            'view_mode': 'tree,form',
            'res_model': 'maintenance.request',
            'type': 'ir.actions.act_window',
            'domain': [('id','in',self.maintenance_ids.ids)],
        })

    def create_maintenance(self):
        return ({
            'name':'Maintenance Request',
            'view_mode': 'form',
            'res_model': 'maintenance.request',
            'type': 'ir.actions.act_window',
            'context': {'default_alert_id':self.id},
        })