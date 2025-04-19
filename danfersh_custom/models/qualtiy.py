from odoo import fields, models, api

from odoo.addons.quality.models.quality import QualityPoint
class QualityPoint(models.Model):
    _name = 'quality.point'

    _inherit = ['quality.point','mail.thread', 'mail.activity.mixin']


class checkQuality(models.Model):
    _inherit = 'quality.check'
    product_id = fields.Many2one(
        'product.product', 'Product', check_company=True, required=False,
        domain="[('type', 'in', ['consu', 'product']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
