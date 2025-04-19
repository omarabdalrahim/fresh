
from odoo import api,fields,models,_

class Partners(models.Model):
    _inherit = "res.partner"

    # url = fields.Char('Url')

    # set sales person of contact by user who create it
    @api.model
    def create(self, vals):
        result = super(Partners, self).create(vals)
        result.user_id = self.env.user.id
        return result