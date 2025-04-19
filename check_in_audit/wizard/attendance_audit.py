
from odoo import api,fields,models,_
from odoo.exceptions import AccessError, MissingError, ValidationError

class AuditAttendanceLine(models.Model):
    _name = "audit.attendance.line"

    control_id = fields.Many2one('quality.point', string="Control Point")
    control_name = fields.Char('Control Name',related='control_id.title',store=True)
    check_id = fields.Many2one('quality.check', string="Check Point")
    pass_bool = fields.Boolean('Pass')
    fail_bool = fields.Boolean('Fail')
    # wiz_id = fields.Many2one('audit.attendance')

    @api.onchange('pass_bool')
    def fail_change(self):
        if self.fail_bool and self.pass_bool:
            self.fail_bool = False

    @api.onchange('fail_bool')
    def pass_change(self):
        if self.fail_bool and self.pass_bool:
            self.pass_bool = False

    def unlink(self):
        print("ddddddddd")
        res = super(AuditAttendanceLine,self).unlink()
        raise ValidationError('يجب التحقق من كل الشروط')



class AttendanceAudit(models.TransientModel):
    _name = "audit.attendance"

    check_ids = fields.Many2many('audit.attendance.line', defualt='get_check_ids',
                                 string='نقاط التحكم المربوطة بالموظف')
    have_audit = fields.Boolean(compute='get_check_ids')
    next_action = fields.Char()
    check_no = fields.Integer()


    def get_check_ids(self):
        print('============')
        employee_checks = self.env['hr.employee'].search([('user_id','=',self.env.uid)]).check_ids
        print('============',employee_checks)
        self.check_no = len(employee_checks)
        if employee_checks:
            print('============', employee_checks)
            self.have_audit=True
            c=[]
            for i in employee_checks:
                c.append((0, 0, {
                    'control_id': i.id,
                }))
            self.check_ids=c
            print(self.check_ids)
        else:
            self.have_audit = False

    def done(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
        pass_no=0
        fail_no=0
        for i in self.check_ids:
            if not i.pass_bool and not i.fail_bool:
                raise ValidationError ('من فضلك قم باختيار كل التحقيقات')
            check_point = self.env['quality.check'].create({
                'point_id': i.control_id.id,
                'test_type_id': i.control_id.test_type_id.id,
                'team_id': i.control_id.team_id.id,
                'company_id': i.control_id.company_id.id,
            })
            if i.pass_bool:
                pass_no+=1
                check_point.quality_state='pass'
            if i.fail_bool:
                fail_no+=1
                check_point.quality_state='fail'
        print('[[[[[[[[[[[[[[[[[[',len(self.check_ids),len(employee.check_ids))
        if  len(self.check_ids) != len(employee.check_ids):
            print('jhhhhhhhhhhhhhhhhhhh')
            raise ValidationError('من فضلك قم باختيار كل التحقيقات برجاء الغلق واعاده المحاولة')
        if pass_no==len(self.check_ids):
            print('[[[[[[[[[[[[[[[[[[',pass_no)
            employee._attendance_action(self.next_action)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            employee._attendance_action(self.next_action)
            employee._attendance_action(self.next_action)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

        # return employee._attendance_action(self.next_action)




