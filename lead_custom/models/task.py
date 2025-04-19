from odoo import fields, models, api,_

class tasks(models.Model):
    _inherit='project.task'
    lead_id = fields.Many2one('crm.lead', string='Lead')


    def action_create_sales(self):

        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context':{'default_x_task_id':self.id,'default_partner_id':self.partner_id.id if self.partner_id else ''},
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_views_sales(self):
        return {
            'name': _('Sales Order'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('x_task_id','=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    @api.model
    def create(self, vals):
        res = super(tasks, self).create(vals)

        if res.x_sale_order_id:
            res.x_sale_order_id.x_count_task+= 1

        if res.x_lead_id:
                res.message_post(
                    body=("Task is created by crm : <a href=# data-oe-model=crm.lead data-oe-id=%d>%s</a>") % (
                        res.x_lead_id.id, res.x_lead_id.name))
        return res

    def action_create_post(self):

        return {
            'name': _('Post'),
            'view_mode': 'form',
            'res_model': 'social.post',
            'context': {'default_x_task_id': self.id, 'default_message': self.name},
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_views_post(self):
        return {
            'name': _('Post'),
            'view_mode': 'tree,form',
            'res_model': 'social.post',
            'domain': [('x_task_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_create_campaigns(self):

        return {
            'name': _('Campaigns'),
            'view_mode': 'form',
            'res_model': 'utm.campaign',
            'context': {'default_x_task_id': self.id, 'default_name': self.name},
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_views_campaigns(self):
        return {
            'name': _('Campaigns'),
            'view_mode': 'tree,form',
            'res_model': 'utm.campaign',
            'domain': [('x_task_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }



