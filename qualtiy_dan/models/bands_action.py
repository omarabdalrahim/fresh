from odoo import fields, models, api


class ModelName(models.Model):
    _name = 'band.action'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']


    name = fields.Char(required=True)
    type_ids = fields.Many2many("band.action.type","band_type","type_id","id",string="الاجراءات المرتبطه")
    active = fields.Boolean(default=True)



class bandType(models.Model):
    _name = 'band.action.type'
    name = fields.Char()

    type = fields.Selection([ \
        ('writen', 'كتابه'), \
        ('photo', 'صوره'), \
        ('file', 'ملف'), \
        ('work', 'اضافه من مركز عمل'), \
        ('employee', 'موظفين'), \
        ('controlpoint', 'نقاط تحكم'), \
        ('coding_action', 'اجراءات التكويد'), \
        ('coding_ins', ' كود التعليمات'), \
        ('code_models', ' النماذج'), \
        ('department', ' الاقسام'), \
        ('revision', 'المراجع'), \
        ('first', 'الصفحه'), \
        ])
    active = fields.Boolean(default=True)