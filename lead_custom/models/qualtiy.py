from odoo import fields, models, api

class ticketcrm(models.Model):
    _inherit='quality.alert'
    x_ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')


