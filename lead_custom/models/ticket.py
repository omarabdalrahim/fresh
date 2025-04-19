from odoo import fields, models, api,_
from odoo.exceptions import ValidationError

class crm_help(models.TransientModel):
    _inherit='crm.lead.convert2ticket'

    def action_lead_to_helpdesk_ticket(self):
        self.ensure_one()
        # get the lead to transform
        lead = self.lead_id
        partner_id = self._find_matching_partner()
        # if not partner_id and (lead.partner_name or lead.contact_name):
        #     partner_id = lead.handle_partner_assignation()[lead.id]
        # create new helpdesk.ticket

        vals = {
            "name": lead.name,
            "description": lead.description,
            "email": lead.email_from,
            "lead_id":self.lead_id.id,
            "x_lead_id":self.lead_id.id,
            "team_id": self.team_id.id,

            "ticket_type_id": self.ticket_type_id.id,
            "partner_id": partner_id or '',
            "user_id": None
        }
        ticket = self.env['helpdesk.ticket'].create(vals)
        lead = self.env['crm.lead'].search([('id', '=', self.lead_id.id)])
        if lead:
             lead.count_ticket += 1
        # move the mail thread
        lead.message_change_thread(ticket)
        # move attachments
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', lead.id)])
        attachments.sudo().write({'res_model': 'helpdesk.ticket', 'res_id': ticket.id})
        # archive the lead
        #lead.write({'active': False})
        # return the action to go to the form view of the new Ticket
        view = self.env.ref('helpdesk.helpdesk_ticket_view_form')
        return {
            'name': _('Ticket created'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'res_id': ticket.id,
            'context': self.env.context
        }



class Ticket(models.Model):
    _inherit = 'helpdesk.ticket'
    lead_id = fields.Many2one('crm.lead', string='Lead')
    x_count_quality = fields.Integer("Count qaultiy", compute='get_count_ticket')


    def action_view_quality(self):
        print('oooo1')
        view = self.env.ref('quality_control.quality_alert_view_form')

        return {
            'name': _('Quailty'),
            'view_mode': 'tree,form',
            'res_model': 'quality.alert',
            'domain': [('ticket_id', '=', self.id)],

            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def create_quality(self):
        print('oooo2')
        quality = self.env['quality.alert'].search([])
        quality.create({

            'sale_order':self.sale_order_id.id if self.sale_order_id else '',
            'ticket_id':self.id,
            'title':self.name,
            'user_id':self.create_uid.id,

            'partner_id': self.partner_id.id if self.partner_id else '',
            'description':self.description,
            'priority':self.priority,

        })
    @api.depends('create_date')
    def get_count_ticket(self):
        for rec in self:
            rec.x_count_quality = 0
            ticket = self.env['quality.alert'].search([('x_ticket_id', '=', self.id)])
            if ticket:
                rec.x_count_quality = len(ticket)

    def create_quality(self):
        print('oooo3',self.message_main_attachment_id.ids)
        view = self.env.ref('quality_control.quality_alert_view_form')
        attachments = self.env['ir.attachment'].search([('res_model','=','helpdesk.ticket'),('res_id','=',self.id)])
        print('oooo3', attachments.ids)
        return {
            'name': _('Ticket'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'quality.alert',
            'type': 'ir.actions.act_window',
            'context': {
                'default_x_ticket_id': self.id,
                'default_name': self.name,
                'default_team_id': self.env['quality.alert.team'].search([], limit=1).id,
                'default_description': self.description,
                'default_attachment_ids': attachments.ids,
            },
            'target': 'current'
        }

    def action_view_quality(self):
        print('oooo4')
        view = self.env.ref('quality.quality_alert_view_tree')
        view_form = self.env.ref('quality_control.quality_alert_view_form')
        orders = self.env['quality.alert'].search([('x_ticket_id', '=', self.id)])
        ids = []
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('Tickets'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            'res_model': 'quality.alert',
            'domain': [('id', 'in', ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    @api.model
    def create(self, vals):
        res = super(Ticket, self).create(vals)
        if res.sale_order_id:
            res.sale_order_id.x_count_ticket += 1
        if res.x_lead_id:
            res.message_post(
                body=("Ticket is created by crm : <a href=# data-oe-model=crm.lead data-oe-id=%d>%s</a>") % (
                    res.x_lead_id.id, res.x_lead_id.name))
        return res
    # @api.constrains('stage_id')
    # def get_stage_id(self):
    #     if self.stage_id.x_lost:
    #         if not self.x_cancal_reason:
    #             raise ValidationError("please Add Reason")
    #
    # def write(self,vals):
    #     res=super(Ticket, self).write(vals)
    #     sale_order = self.env['sale.order'].search([('x_ticket_id', '=', self.id)])
    #     if self.stage_id.x_fake:
    #
    #         if sale_order:
    #             sale_order.action_cancel()
    #     if self.stage_id.x_won:
    #         stage_id=self.env['helpdesk.stage'].search([('is_close','=',True)],limit=1)
    #         if stage_id:
    #             self.stage_id=stage_id.id
    #             if sale_order:
    #                 sale_order.action_confirm()
    #     if self.stage_id.x_lost:
    #
    #         stage_id = self.env['helpdesk.stage'].search([('x_preview', '=', True)], limit=1)
    #         self.stage_id=stage_id.id
    #         if sale_order:
    #             sale_order.action_cancel()
    #             sale_order.message_post(
    #                 body=("Ticket is losted by %s  <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
    #                     self.x_cancal_reason,self.id, self.name))
    #     return res






    def action_create_sales(self):

        return {
            'name': _('Sales Order'),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'context':{'default_x_ticket_id':self.id,'default_partner_id':self.partner_id.id if self.partner_id else ''},
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_views_sales(self):
        return {
            'name': _('Sales Order'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('x_ticket_id','=', self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }
