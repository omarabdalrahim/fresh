from odoo import  api,fields,models

class UserUU(models.Model):
    _inherit = 'res.users'

    equipment_count = fields.Integer()