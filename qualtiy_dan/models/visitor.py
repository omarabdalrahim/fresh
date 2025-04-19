from odoo import fields, models, api,_
from odoo.exceptions import RedirectWarning, UserError, ValidationError
from datetime import datetime
class VistorPurpose(models.Model):
    _name = "visit.purpose"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)


class Visitor(models.Model):
    _name = 'visitor.question'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Description'
    active = fields.Boolean(default=True)

    company_name = fields.Many2one("res.partner", string="اسم الجهه ", domain="[('is_company','=',True)]")
    vistor_id = fields.Many2one("res.partner", required=True, string="اسم الزائر ",
                                domain="[('parent_id','=',company_name),('type','=','private')]")
    purpose = fields.Many2one("visit.purpose", required=True, string="الغرض")
    other_person = fields.Many2one("hr.employee", string="المرافق ")
    date_time = fields.Datetime("التاريخ", default=lambda self: fields.datetime.now())
    function = fields.Char(related='vistor_id.function', store=True)

    name = fields.Char("التسلسل ")
    line_ids = fields.One2many('visitor.question.line', 'parent_id')
    notes = fields.Text(default="""نطلب منك اللتزام بسياستنا و إجراءاتنا . يحظر ما يلي في صالت النتاج:
1.منع ارتداء اي مجوهرات )ساعه و اقراط و أساور و دبابيس ربطات العنق ....وما الي ذلك( 
2.تج نب الطعام و الشراب في صالت النتاج 
3.ل يسمح بدخول الموبايل او معدات للتصوير د اخل الصالت 
4.الزجاج و البالستيك الصلب ممنوع داخل الصالت . يجب علي الزوار الذين يرتدون نظارات او عدسات لصقه
إبالغ المرافق علي الفور إذا تم اي كسر او اي خساره
5.ممنوع دخول اي صاله او مخزن بدون ارتداي اوفر شوز و هيرنت وكمامه""")

    acceces_not = fields.Text(default=""""يرجي مالحظه القواعد التالي ه: 
في حاله نشوب حريق يرجي مغادره المبني من أقرب مخرج 
توخي الحذر من المعدات التي يتم تشغيلها في الصالات
يجب مرافقه المرافق في جميع الوقات 
يطلب م ن الزوار الغير معلنين إبراز هويه رسميه قبل الدخول الي المنشأه """)
    visitor_sign = fields.Binary("توقيع الزائر")
    other_sign = fields.Binary("توقيع المرافق")
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 copy=False, required=True,
                                 default=lambda self: self.env.company, )

    @api.model
    def create(self, vals):
        res = super(Visitor, self).create(vals)
        res.name = self.env["ir.sequence"].next_by_code("visitor")
        message = self.env['mail.mail'].search([])
        # mail_values = {
        #     'author_id': self.env.user.partner_id.id,
        #     'body_html': "شكرا علي زياراتكم",
        #     'email_from': (
        #             self.company_id.partner_id.email_formatted
        #             or self.env.user.email_formatted
        #             or self.env.ref('base.user_root').email_formatted
        #     ),
        #     'email_to': res.vistor_id.email,
        #
        #     'state': 'outgoing',
        #     'subject': "Visit Danfresh",
        # }
        self.env['mail.mail'].create(dict(
            subject=_('Visit Danfresh'),
            body_html="شكرا علي زياراتكم",
            email_from="info@danjuice.com",
            email_to=res.vistor_id.email,
        )).send()
        # message.sudo().create(mail_values)
        # message.sudo().send()
        return res
    @api.constrains('line_ids')
    def check_lines(self):
        for rec in self.line_ids:
            if not rec.check and not rec.no:
                raise ValidationError("من فضلك اجب عن جميع الاسئله")

    @api.onchange('name')
    def onchnage_data(self):
        print("=======================================")
        if not self.line_ids:
            self.line_ids = [
                (0, 0, {'name': "هل عانيت خالل اليام السبعه الماضيه من القئ و السهال او التهاب المعده"}),
                (0, 0, {'name': "هل كنت علي اتصال بشخص يعاني من المراض المذكوره ؟"}),
                (0, 0, {'name': "هل عانيت من اي التهابات جلد يه؟ "}),
                (0, 0, {'name': "هل تعاني من اي التهاب في الذن او النف ا و الحلق؟"}),
                (0, 0, {'name': """ 
                هل تتناول حاليا اي دواء؟
                لا يمكن تناول الادويه ف مناطق الانتاج
    """}),
                (0, 0, {'name': 'هل سافرت الي الخارج في السابيع الربعه الماضيه؟ '}),
                (0, 0, {'name': 'إذا كانت الجابه نعم .يمكنك كتابه اسم البلد او البلدان التي قمت بزيارتها '})
            ]


class VisitorLine(models.Model):
    _name = 'visitor.question.line'
    name = fields.Char(required=True)
    check = fields.Boolean("نعم")
    no = fields.Boolean("لا")
    parent_id = fields.Many2one('visitor.question')
    active = fields.Boolean(default=True)
