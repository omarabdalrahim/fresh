from odoo import fields, models, api

class ModelName(models.Model):
    _inherit = 'mrp.report'

    x_categ_id = fields.Many2one("product.category")

    def _select(self):
        res = super()._select()
        res+=",mo.x_categ_id as x_categ_id"

        return res

    def _group_by(self):
        res = super()._group_by()
        res += """,
               mo.x_categ_id
               """
        return res
