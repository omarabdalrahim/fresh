
from odoo import api,fields,models,_

class Partners(models.Model):
    _inherit = "hr.employee"

    check_ids = fields.Many2many('quality.point',string='نقاط التحكم المربوطة بالموظف')

    def attendance_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        attendance_user_and_no_pin = self.user_has_groups(
            'hr_attendance.group_hr_attendance_user,'
            '!hr_attendance.group_hr_attendance_use_pin')
        can_check_without_pin = attendance_user_and_no_pin or (self.user_id == self.env.user and entered_pin is None)
        if can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin:
            print('-------------------',self.attendance_state)
            if self.attendance_state != 'checked_in'and self.check_ids:
                print('-------------------', self.check_ids)
                form_view_id = self.env.ref('check_in_audit.attendance_audit_form_view').id
                c = []
                for i in self.check_ids:
                    c.append((0, 0, {
                        'control_id': i.id,
                    }))
                print('-------------------', c)
                return{
                    # 'type': 'ir.actions.act_window',
                    # 'name': 'برجاء التحقق من',
                    # 'view_mode': 'form',
                    # 'res_model': 'audit.attendance',
                    # 'context': {'default_next_action': next_action},
                    'view_id': form_view_id,
                    'checks':c,
                    'next_action':next_action
                }

            return self._attendance_action(next_action)
        if not self.user_has_groups('hr_attendance.group_hr_attendance_user'):
            return {'warning': _(
                'To activate Kiosk mode without pin code, you must have access right as an Officer or above in the Attendance app. Please contact your administrator.')}
        return {'warning': _('Wrong PIN')}