
from odoo import api,fields,models,_
from datetime import datetime, timedelta
from odoo.exceptions import AccessError, MissingError, ValidationError

class AuditType(models.Model):
    _name = "audit.type"

    name = fields.Char('name')

class Division(models.Model):
    _name = "division"

    name = fields.Char('name')

class Branches(models.Model):
    _name = "branch"

    name = fields.Char('name')
    division_ids = fields.Many2many('division',string="Divisions")
    tags = fields.Many2many('quality.tag',String='Tags')
    user_id = fields.Many2many('res.users', string="Responsible")




class Audit(models.Model):
    _name = "audit"
    _rec_name="code"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']


    name = fields.Char('name')
    code = fields.Char('Code',default='/')
    @api.model
    def create(self, vals):
        print('jjjjjjjjjjjj',vals)
        print('jjjjjjjjjjjj',self)
        res = super(Audit, self).create(vals)
        res.code = self.env["ir.sequence"].next_by_code("audit")
        return res

    date= fields.Date('Date',default=lambda  self: fields.Date.today())



    time= fields.Float('Time')
    time_date= fields.Datetime('Time' ,default=lambda  self: fields.Datetime.now())
    user_id = fields.Many2one('res.users', string="Examiner", default=lambda self: self.env.user.id)
    res_id = fields.Many2many('res.users', string="Responsible")
    audit_type_id = fields.Many2one('audit.type', string="Type")
    branch_id = fields.Many2one('branch', string="Branches")
    division_ids = fields.Many2many('division', string="Divisions")
    tags = fields.Many2many('quality.tag', String='Tags')
    line_ids = fields.One2many(comodel_name='audit.line',
                               string='Lines',
                               inverse_name='audut_id')


    @api.onchange('branch_id')
    def set_branch_info(self):
        print('-------------------->')
        if self.branch_id:
            print('-------------------->',self.branch_id,self.branch_id.division_ids)
            self.division_ids = self.branch_id.division_ids
            print('-------------------->', self.division_ids)
            self.tags = self.branch_id.tags
            self.res_id=self.branch_id.user_id
            controls= self.env['quality.point'].search([('branch_id','=',self.branch_id.id)])
            c=[]
            self.line_ids.unlink()
            print('controls',controls)
            no=1
            for i in controls:
                # check_point = self.env['quality.check'].create({
                #     'point_id': i.id,
                #     'test_type_id': i.test_type_id.id,
                #     'team_id': i.team_id.id,
                #     'company_id': i.company_id.id,
                # })
                c.append((0,0,{
                'control_id': i,
                    'audut_id':self.id,
                    # 'check_id':check_point.id,
                    'serial':no
                }))
                no+=1
            print(c)
            self.line_ids=c
        else:
            self.division_ids = False
            self.tags = False
            self.res_id = False
            self.line_ids.unlink()

    @api.onchange('res_id','branch_id')
    def check_on_res(self):
            print('pppppppppppp',self.branch_id.user_id.ids)
            return {
                'domain': {'res_id': [('id', 'in',self.branch_id.user_id.ids )]}
            }

    def return_check_points(self):
        check = self.line_ids.mapped('check_id')
        print(check)
        return {
            'name': 'Check Points',
            'view_mode': 'tree',
            'view_id': False,
            'res_model': 'quality.check',
            'domain': [('id', 'in', check.ids)],
            'type': 'ir.actions.act_window',
        }



class Alert(models.Model):
    _inherit = "quality.alert"

    attachment_ids = fields.Many2many(string="Image", comodel_name='ir.attachment', index=True,)


class AuditLine(models.Model):
    _name = "audit.line"

    audut_id = fields.Many2one('audit', string="Audit")
    control_id = fields.Many2one('quality.point', string="Control Point")
    control_name = fields.Char('Control Name',related='control_id.title')
    alert_id = fields.Many2one('quality.alert', string="Quality Alert")
    check_id = fields.Many2one('quality.check', string="Check Point")
    pass_bool = fields.Boolean('Pass')
    fail_bool = fields.Boolean('Fail')
    comment = fields.Char('Comment')
    attachment_ids = fields.Many2many(string="Image", comodel_name='ir.attachment', index=True,
                                                 copy=False)
    serial = fields.Integer('Serial')

    @api.onchange('comment')
    def change_comment(self):
        if self.fail_bool and self.alert_id:
            self.alert_id.description = self.comment

    @api.onchange('attachment_ids')
    def change_attachment(self):
        print('sdsdsdsadada')
        if self.fail_bool and self.alert_id:
            print('sdsdsdsadad2222a',self.attachment_ids)
            self.alert_id.attachment_ids += self.attachment_ids

    @api.onchange('pass_bool')
    def pass_check(self):
        print('----------l>')
        if self.pass_bool:
            self.fail_bool = False
            if self.alert_id:
                self.alert_id.unlink()
            if self.check_id:
                self.check_id.quality_state = 'pass'
            else:
                self.check_id = self.env['quality.check'].create({
                    'point_id': self.control_id.id,
                    'test_type_id': self.control_id.test_type_id.id,
                    'team_id': self.control_id.team_id.id,
                    'company_id': self.control_id.company_id.id,
                    'quality_state':'pass'
                })
            # self.check_id.quality_state='pass'
        else:
            if not self.pass_bool and not self.fail_bool:
                self.check_id.unlink()
            # self.check_id.quality_state = 'none'

    @api.onchange('fail_bool')
    def fail_check(self):
        print('----------lo>')
        if self.fail_bool:
            self.pass_bool=False
            if self.check_id:
                self.check_id.quality_state = 'fail'
                alert = self.env['quality.alert'].create({
                    'check_id': self.check_id.id,
                    'team_id': self.check_id.team_id.id,
                    'company_id': self.check_id.company_id.id,
                    'description': self.comment
                })
                self.alert_id = alert
            else:
                self.check_id= self.check_id = self.env['quality.check'].create({
                    'point_id': self.control_id.id,
                    'test_type_id': self.control_id.test_type_id.id,
                    'team_id': self.control_id.team_id.id,
                    'company_id': self.control_id.company_id.id,
                    'quality_state':'fail'
                })
                alert = self.env['quality.alert'].create({
                    'check_id': self.check_id.id,
                    'team_id': self.check_id.team_id.id,
                    'company_id': self.check_id.company_id.id,
                    'description':self.comment
                })
                self.alert_id=alert
        else:
            self.alert_id.unlink()
            if not self.pass_bool and not self.fail_bool:
                self.check_id.unlink()

