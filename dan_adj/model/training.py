
from odoo import api,fields,models,_
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, MissingError, ValidationError


class Traning(models.Model):
    _name = "training"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name="code"

    name = fields.Char('name')
    code = fields.Char('Code',default='/')
    @api.model
    def create(self, vals):

        res = super(Traning, self).create(vals)
        res.code = self.env["ir.sequence"].next_by_code("training")
        return res

    date= fields.Date('التاريخ',default=lambda  self: fields.Date.today())
    type = fields.Selection([
        ('a', 'وقائي'),
        ('b', 'تصحيحي')], 'نوع', track_visibility='always',
        default=lambda self: self._context.get('type_doc', 'ctt_ett'))

    employee_id = fields.Many2one('hr.employee', string="المواظف")
    control_ids = fields.Many2many('quality.point', string='نقاط التحكم' )
    check_ids = fields.Many2many('quality.check', string='نقاط لفحص' )
    alert_ids = fields.Many2many('quality.alert', string='التنبيهات' )

    notes = fields.Text ('ماتم تدريب الموظف عليه')

    employee_sign_name = fields.Char('توقيع بواسطة')
    manager_sign_name = fields.Char('توقيع بواسطة')

    date_employee_sign = fields.Date('تاريخ التوقيع')
    date_manager_sign = fields.Date('تاريخ التوقيع')

    employee_sign = fields.Binary(string='التوقيع ')
    manager_sign = fields.Binary(string='التوقيع ')

    control_note= fields.Html()
    control_reason= fields.Html()
    control_message= fields.Html()

    alert_desc = fields.Html()
    alert_corrective = fields.Html()
    alert_preve = fields.Html()


    @api.onchange('control_ids')
    def get_notes(self):
        self.control_note=self.control_message= self.control_reason=''
        for i in self.control_ids:
            if i.note:
                if i.title:
                    self.control_note += i.name + " - " + i.title
                else:
                    self.control_note += i.name
                self.control_note+=i.note
            if i.reason:
                if i.title:
                    self.control_reason += i.name + " - " + i.title
                else:
                    self.control_reason += i.name
                self.control_reason += i.reason
            if i.failure_message:
                if i.title:
                    self.control_message += i.name + " - " + i.title
                else:
                    self.control_message += i.name
                self.control_message+=i.failure_message


    @api.onchange('alert_ids')
    def get_alert(self):
        self.alert_desc = self.alert_corrective = self.alert_preve = ''
        for i in self.alert_ids:
            if i.description:
                self.alert_desc += i.name
                self.alert_desc += i.description
            if i.action_corrective:
                self.alert_corrective += i.name
                self.alert_corrective += i.action_corrective
            if i.action_preventive:
                self.alert_preve += i.name
                self.alert_preve += i.action_preventive

