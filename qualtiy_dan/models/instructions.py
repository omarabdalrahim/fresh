from odoo import fields, models, api


class Instruction(models.Model):
    _name = 'band.instruction'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)

    name = fields.Char(required=True)
    code = fields.Char()
    work_description = fields.Char()
    work_description = fields.Date(default=lambda self: fields.datetime.now().date())
    position_create = fields.Char("prepared Position")
    sign_create = fields.Binary()
    sign_date = fields.Date(default=lambda self: fields.datetime.now().date())
    previewed_by = fields.Many2one("hr.employee")

    sign_previewed = fields.Binary()
    date_previewed = fields.Date()
    action_id = fields.Many2one("action.coding",required=True,string="اسم الاجراء")
    model_action_id = fields.Many2one("model.coding",string="النموذج",required=True,domain="[('coding_id','=',action_id)]")
    standards = fields.Char()
    certificate = fields.Char()

