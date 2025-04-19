from odoo import fields, models, api


class qualitypoint(models.Model):
    _inherit = 'quality.point'
    coding_id = fields.Many2one('action.coding',string="تكويد الاجراء")
    model_coding_id = fields.Many2one('action.coding',string="تكويد النموذج",domain=[('coding_id','=',coding_id)])
class qualitycheck(models.Model):
    _inherit = 'quality.check'
    coding_id = fields.Many2one(related='point_id.coding_id',string="تكويد الاجراء",store=True)
    model_coding_id = fields.Many2one(related='point_id.model_coding_id',string="تكويد النموذج",store=True,domain=[('coding_id','=',coding_id)])
