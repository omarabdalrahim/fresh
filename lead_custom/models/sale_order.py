from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)
class sale_order(models.Model):
    _inherit = 'sale.order'


    def action_view_task(self):
        return {
            'name': _('Task'),
            'view_mode': 'tree,form',
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'domain': [('x_sale_order_id','=', self.id)],
            'target': 'current'
        }
    def create_task(self):
        view = self.env.ref('project.view_task_form2')
        return {
            'name': _('Task'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'context': {'default_x_sale_order_id': self.id,'default_project_sale_order_id': self.id,'default_partner_id':self.partner_id.id if self.partner_id else ''},
            'target': 'current'
        }
    def action_view_ticket(self):
        return {
            'name': _('Tickets'),
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'domain': [('sale_order_id','=', self.id)],
            'target': 'current'
        }
    def create_ticket(self):
        view = self.env.ref('helpdesk.helpdesk_ticket_view_form')
        return {
            'name': _('Tickets'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'context': {'default_sale_order_id': self.id,'default_partner_id':self.partner_id.id if self.partner_id else '' },
            'target': 'current'
        }





    @api.model
    def create(self, vals):
        res = super(sale_order, self).create(vals)
        if res.x_task_id:
            res.x_task_id.x_count_sale += 1

            res.message_post(
                body=("Sales Oder Create From Task: <a href=# data-oe-model=project.task data-oe-id=%d>%s</a>") % (
                    res.x_task_id.id, res.x_task_id.name),
                message_type='comment', )
        if res.x_ticket_id:
            res.message_post(
                body=("Sales Oder Create From Ticket: <a href=# data-oe-model=helpdesk.ticket data-oe-id=%d>%s</a>") % (
                    res.x_ticket_id.id, res.x_ticket_id.name),
                message_type='comment', )
        return res
