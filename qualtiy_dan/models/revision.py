from odoo import fields, models, api


class Revision(models.Model):
    _name = 'page.revision'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']



    name = fields.Char(required=True)
    url = fields.Char(required=True,string="اللينك")
    other = fields.Char(required=True,string="الارفاق")
    active = fields.Boolean(default=True)
