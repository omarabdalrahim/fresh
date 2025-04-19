from odoo import fields, models, api

import itertools
class MachineDep(models.Model):
    _name = 'machine.dep'

    name = fields.Char('القسم')


class Machine(models.Model):
    _name = 'machine'

    name = fields.Char('المعده')


class MachineType(models.Model):
    _name = 'machine.type'

    name = fields.Char('النوع')


class OperationType(models.Model):
    _name = 'operation.type'

    name = fields.Char('العملية')

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    machine_dep_id = fields.Many2one('machine.dep','اقسام المكنة')
    machine_id = fields.Many2one('machine','المعده')
    machine_type_id = fields.Many2one('machine.type','نوع المعده')
    operation_type_id = fields.Many2one('operation.type','نوع العملية')