from odoo import api, fields, models, _



from odoo.exceptions import ValidationError
class ticket(models.Model):
    _inherit = 'crm.lead'
    count_ticket = fields.Integer("Count Ticket",compute='get_count_ticket')
    count_task = fields.Integer("Count Tasks",compute='get_count_task')

    @api.constrains('stage_id')
    def get_stage_id(self):
        for rec in self:
            if rec.stage_id.x_lost:
                if not rec.x_cancal_reason:
                    raise ValidationError("please Add Reason")

    def write(self, vals):
        res = super(ticket, self).write(vals)
        for rec in self:
            tickets= self.env['helpdesk.ticket'].search([('x_lead_id','=',rec.id)])
            if rec.stage_id.x_fake:
                for rec in tickets:
                    stage_id = self.env['helpdesk.stage'].search([('x_lost','=',True)],limit=1)
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>.",stage_id)
                    if stage_id:
                        rec.stage_id=stage_id.id
                    sale_order = self.env['sale.order'].search([('x_ticket_id', '=', rec.id)])
                    for order in sale_order:
                        order.action_cancel()
            if rec.stage_id.x_won:
                for rec in tickets:
                    stage_id = self.env['helpdesk.stage'].search([('x_won','=',True)],limit=1)
                    if stage_id:
                        rec.stage_id=stage_id.id
                    sale_order = self.env['sale.order'].search([('x_ticket_id', '=', rec.id)])
                    for order in sale_order:
                        order.action_confirm()

            if rec.stage_id.x_lost:
                for rec in tickets:
                    stage_id = self.env['helpdesk.stage'].search([('x_preview','=',True)],limit=1)
                    if stage_id:
                        rec.stage_id=stage_id.id
                    sale_order = self.env['sale.order'].search([('x_ticket_id', '=', rec.id)])
                    for order in sale_order:
                        order.action_cancel()
                        order.message_post(
                            body=("Lead is losted by %s  <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                                rec.x_cancal_reason, rec.id, rec.name))



        return res


    @api.depends('type')
    def get_count_ticket(self):
        for rec in self:
            rec.count_ticket=0
            ticket = self.env['helpdesk.ticket'].search([('lead_id','=',rec.id)])
            if ticket:
                rec.count_ticket = len(ticket)

    @api.depends('type')
    def get_count_task(self):
        for rec in self:
            rec.count_task = 0
            ticket = self.env['project.task'].search([('lead_id', '=', rec.id)])
            if ticket:
                rec.count_task = len(ticket)



    def action_view_ticketes(self):
        view = self.env.ref('helpdesk.helpdesk_tickets_view_tree')
        view_form=self.env.ref('helpdesk.helpdesk_ticket_view_form')
        orders=self.env['helpdesk.ticket'].search([('lead_id','=',self.id)])
        ids=[]
        for rec in orders:
            ids.append(rec.id)
        return {
            'name': _('Tickets'),
            'view_mode': 'tree,form',
            'view_type':'form',
            'views': [(view.id,'tree'),(view_form.id,'form')],
            'res_model': 'helpdesk.ticket',
            'domain':[('id','in',ids)],
            'type': 'ir.actions.act_window',
            'target':'current'
        }


    def action_view_task(self):

        return {
            'name': _('Tasks'),
            'view_mode': 'tree,form',


            'res_model': 'project.task',
            'domain':[('lead_id','=',self.id)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def create_task(self):
        view = self.env.ref('project.view_task_form2')

        return {
            'name': _('Tasks'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'context': {'default_lead_id': self.id,
                        'default_x_lead_id': self.id,
                        'default_name': self.name
                        },
            'target': 'current'
        }
    def create_ticket(self):
        view = self.env.ref('helpdesk.helpdesk_ticket_view_form')

        return {
            'name': _('Tasks'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
            'context': {'default_lead_id': self.id,
                        'default_x_lead_id': self.id,
                        'default_name':self.name,
                        'default_partner_id':self.partner_id.id if self.partner_id else '',
                        },
            'target': 'current'
        }