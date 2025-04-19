from odoo import api,fields,models

class EmployeeT(models.Model):
    _inherit = 'hr.employee'

    equipment_count = fields.Integer(string="Equipment Count")
