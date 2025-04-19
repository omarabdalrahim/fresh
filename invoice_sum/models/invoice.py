from odoo import api, models
class invoice(models.Model):
    _inherit='account.move'
    def action_post_invoice(self):
        for rec in self:
            rec.state='posted'
