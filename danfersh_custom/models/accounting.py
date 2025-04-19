from odoo import fields, models, api


class Move(models.Model):
    _inherit = "account.move"

    # def write(self,vals):
    #     res = super(Move,vals).write(vals)
    #     for rec in self.invoice_line_ids
