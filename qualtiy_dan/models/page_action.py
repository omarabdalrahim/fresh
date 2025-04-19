from odoo import fields, models, api
from odoo.addons.website.tools import text_from_html

class ActionPage(models.Model):
    _name = 'page.action.first'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    _description = 'Description'
    name = fields.Char()
    active = fields.Boolean(default=True)
    name_arabic = fields.Char()
    action_id = fields.Many2one("action.coding", "كود الاجراء")
    export_date = fields.Date("تاريخ الاصدار", default=lambda self: fields.datetime.now().date())
    export_name = fields.Char("رقم الاصدار")
    page = fields.Integer("عدد الصفحات")
    date = fields.Date("تاريخ تفعيل النظام", default=lambda self: fields.datetime.now().date())
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 copy=False, required=True,
                                 default=lambda self: self.env.company, )
    logo = fields.Binary("Logo", related="company_id.logo")
    stamp = fields.Binary("Stamp", related="company_id.x_stamp")

    editor_name = fields.Many2one("hr.employee", "اعداد")
    revision_name = fields.Many2one("hr.employee", "مراجع")
    approved_name = fields.Many2one("hr.employee", "اعتماد")
    job_editor_name = fields.Char("وظيفه الاعداد")
    job_revision_name = fields.Char(" وظيفه مراجع")
    job_approved_name = fields.Char(" وظيفه اعتماد")
    sign_editor_name = fields.Binary("توقيع الاعداد")
    sign_revision_name = fields.Binary(" توقيع مراجع")
    sign_approved_name = fields.Binary(" توقيع اعتماد")
    lines = fields.One2many("page.lines","parent_id")

    @api.onchange('action_id')
    def _onchange_action_id(self):
        ids = []
        if self.action_id:
            self.action_id.get_first_page_id()

            if self.action_id.bands_ids:
                values = []
                self.lines=[]
                for rec in self.action_id.bands_ids:
                    values.append((0,0,{
                        'name':rec.id,
                        'type_ids':[(4,type.id) for type in rec.type_ids],
                        'writen_check': True if self.env['band.action.type'].search([('type','=','writen')],limit=1) in rec.type_ids else False,
                        'photo_check': True if self.env['band.action.type'].search([('type','=','photo')],limit=1) in rec.type_ids else False,
                        'file_check': True if self.env['band.action.type'].search([('type','=','file')],limit=1) in rec.type_ids else False,
                        'work_check': True if self.env['band.action.type'].search([('type','=','work')],limit=1) in rec.type_ids else False,
                        'employee_check': True if self.env['band.action.type'].search([('type','=','employee')],limit=1) in rec.type_ids else False,
                        'controlpoint_check': True if self.env['band.action.type'].search([('type','=','controlpoint')],limit=1) in rec.type_ids else False,
                        'coding_action_check': True if self.env['band.action.type'].search([('type','=','coding_action')],limit=1) in rec.type_ids else False,
                        'coding_ins_check': True if self.env['band.action.type'].search([('type','=','coding_ins')],limit=1) in rec.type_ids else False,
                        'code_models_check': True if self.env['band.action.type'].search([('type','=','code_models')],limit=1) in rec.type_ids else False,
                        'department_check': True if self.env['band.action.type'].search([('type','=','department')],limit=1) in rec.type_ids else False,
                        'revision_check': True if self.env['band.action.type'].search([('type','=','revision')],limit=1) in rec.type_ids else False,
                        'first_check': True if self.env['band.action.type'].search([('type','=','first')],limit=1) in rec.type_ids else False,

                    }))
                self.lines=values
        for rec in self.env['page.action.first'].search([]):
            ids.append(rec.action_id.id)
        return {
            'domain': {'action_id': [('id', 'not in', ids)]}
        }

    # def write(self,vals):
    #     res = super(ActionPage,self).write(self)
    #     self.action_id.get_first_page_id()
    #     return res




    @api.onchange('action_id')
    def _ochnage_actin_id(self):
        if self.action_id:
            self.name = self.action_id.name
            self.name_arabic = self.action_id.name_arabic


class bandlines(models.Model):
    _name = "page.lines"
    all_name = fields.Text(compute='get_allname',)


    parent_id = fields.Many2one("page.action.first")
    name = fields.Many2one("band.action", required=True)
    type_ids = fields.Many2many("band.action.type", "band_page", "type_id", "id", string="الاجراءات المرتبطه")
    type = fields.Selection([ \
        ('writen', 'كتابه'), \
        ('photo', 'صوره'), \
        ('file', 'ملف'), \
        ('work', 'اضافه من مركز عمل'), \
        ('employee', 'موظفين'), \
        ('controlpoint', 'نقاط تحكم'), \
        ('coding_action', 'اجراءات التكويد'), \
        ('coding_ins', ' كود التعليمات'), \
        ])
    writen = fields.Text("كتابه")
    photo = fields.Binary("صوره")
    file = fields.Binary("ملف")


    work = fields.Many2one("mrp.workcenter",string="اضافه من مركز عمل")
    work_ids = fields.Many2many("mrp.workcenter", string="اضافه من مركز عمل")
    employee = fields.Many2many("hr.employee",string="موظفين")
    controlpoint = fields.Many2many("quality.point",string="نقاط تحكم")
    coding_action = fields.Many2many("action.coding",string="اجراءات التكويد")
    coding_ins = fields.Many2many("model.instruction",string=" كود التعليمات")
    active = fields.Boolean(default=True)


    code_models = fields.Many2many("model.coding",string="النماذج")
    department = fields.Many2many("hr.department",string="النماذج")
    revision = fields.Many2many("page.revision",string="المراجع")
    first = fields.Many2many("page.action.first",string="الصفحه")

    @api.depends('name','first', 'department','revision','code_models','writen', 'work', 'employee', 'controlpoint', 'coding_action', 'coding_ins')
    def get_allname(self):
        for rec in self:
            rec.all_name = rec.name.name + "\n" if rec.name else ''
            if rec.writen:
                rec.all_name+=str(rec.writen)
            if rec.work:
                    rec.all_name+= rec.work.name + "\n"
            if rec.employee:
                for line in rec.employee:
                    rec.all_name+= line.name + "\n"
            if rec.controlpoint:
                for line in rec.controlpoint:
                    rec.all_name+= line.name + "\n"
            if rec.coding_action:
                for line in rec.coding_action:
                    rec.all_name+= line.name + "\n"
            if rec.coding_ins:
                for line in rec.coding_ins:
                    rec.all_name+= line.name + "\n"
            if rec.code_models:
                for line in rec.code_models:
                    rec.all_name+= line.name + "\n"
            if rec.department:
                for line in rec.department:
                    rec.all_name+= line.name + "\n"
            if rec.revision:
                for line in rec.revision:
                    rec.all_name+= line.name + "\n"
            if rec.first:
                for line in rec.first:
                    rec.all_name+= line.name + "\n"

    writen_check = fields.Boolean("")
    photo_check = fields.Boolean("")
    file_check = fields.Boolean("")
    work_check = fields.Boolean( "")
    employee_check = fields.Boolean("")
    controlpoint_check = fields.Boolean(" ")
    coding_action_check = fields.Boolean(" ")
    coding_ins_check = fields.Boolean(" ")
    code_models_check = fields.Boolean(" ")
    department_check = fields.Boolean(" ")
    revision_check = fields.Boolean(" ")
    first_check = fields.Boolean(" ")