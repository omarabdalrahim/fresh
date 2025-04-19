from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    quality_control_point_qty = fields.Float(string="Quality Control Points")
