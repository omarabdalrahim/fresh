from odoo import api, fields, models, _
from datetime import datetime, timedelta


class Week(models.Model):
    _name = "days"
    name = fields.Char('name')


class QualityType(models.Model):
    _name = 'quality.type'
    name = fields.Char('Type name')


class QualityPoint(models.Model):
    _inherit = "quality.alert"
    reason = fields.Char()
    branch_id = fields.Many2one('branch', string="Branches")


class QualityPoint(models.Model):
    _inherit = "quality.point"

    measure_frequency_unit = fields.Selection(selection_add=[('shift', 'Shift'),
                                                             ('hour', 'Hour'),
                                                             ('p_days', 'Periodic Days')])

    quality_type_id = fields.Many2one('quality.type', string='Quality Type')
    equipment_id = fields.Many2one('maintenance.equipment.category', string='Equipment')
    days_ids = fields.Many2many('days', string='Days')
    add_related_points = fields.Boolean(compute='change_point_related')
    quality_control_related_ids = fields.Many2many('quality.point', 'many_quialty_points', 'control_id', 'point_id',
                                                   string='Quality Point Related')

    job_position_id = fields.Many2many('hr.job', string='المسمي الوظيفي')

    many_user_id = fields.Many2many('res.users', string='Responsibles')
    fail_many_user_id = fields.Many2many('res.users', 'fail_users', string='مسئولين تنبيهات الجوده')
    auto_check_point_day = fields.Boolean(string='Automatic create check points')
    auto_check_point = fields.Boolean(string='Automatic create check points')
    next_create_time = fields.Datetime(string='Next Check at')
    last_create_time = fields.Datetime(string='last Check at')
    picking_type_ids = fields.Many2many(
        'stock.picking.type', string='Operation Types', required=False, check_company=True)

    branch_id = fields.Many2one('branch', string="Branches")
    division_ids = fields.Many2many('division', string="Divisions")
    tags = fields.Many2many('quality.tag', String='Tags')

    def name_get(self):
        return [(rec.id, "%s - %s" % (rec.name, rec.title)) for rec in self]

    def get_alerts(self):
        alerts = self.check_ids.mapped('alert_ids')
        return ({
            'name': _('Alerts'),
            'view_mode': 'tree',
            'res_model': 'quality.alert',
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', alerts.ids)],
        })

    @api.depends('picking_type_ids')
    def change_point_related(self):
        print('ppppppppppppppppppppppppppppp')
        # if self.picking_type_ids and self.company_id.add_related_control_point:
        if self.company_id.add_related_control_point:
            print('ppppppppppppppppppppppppppppp2')
            self.add_related_points = True
        else:
            print('ppppppppppppppppppppppppppppp3')
            self.add_related_points = False

    @api.onchange('branch_id')
    def set_branch_info(self):
        print('-------------------->')
        if self.branch_id:
            self.division_ids = self.branch_id.division_ids
            self.tags = self.branch_id.tags

    def set_next_create_time(self, result):
        print('time-->', result.measure_frequency_unit, result.measure_frequency_unit_value)
        if result.measure_frequency_unit == 'hour':
            result.next_create_time = fields.Datetime.now() + timedelta(hours=result.measure_frequency_unit_value)
        elif result.measure_frequency_unit == 'shift' :
            result.next_create_time = fields.Datetime.now() + timedelta(hours=result.measure_frequency_unit_value * 8)
        elif result.measure_frequency_unit == 'day':
            result.next_create_time = fields.Datetime.now() + timedelta(days=result.measure_frequency_unit_value)
        elif result.measure_frequency_unit == 'week' :
            result.next_create_time = fields.Datetime.now() + timedelta(
                weeks=result.measure_frequency_unit_value)
        elif result.measure_frequency_unit == 'month' :
            result.next_create_time = fields.Datetime.now() + timedelta(
                months=result.measure_frequency_unit_value)

    @api.model
    def create(self, vals):
        result = super(QualityPoint, self).create(vals)
        if result.auto_check_point:
            self.last_create_time = fields.Datetime.now()
            self.set_next_create_time(result)
            self.corn_create_check_point()
        return result

    @api.onchange('auto_check_point', 'measure_frequency_unit', 'measure_frequency_unit_value')
    def change_auto_check_point(self):
        if self.auto_check_point:
            self.set_next_create_time(self)
            self.last_create_time = fields.Datetime.now()
        else:
            self.next_create_time = False

    def if_create_new(self, diff, result):
        if result.measure_frequency_unit == 'hour' and (diff >= result.measure_frequency_unit_value):
            return True
        elif result.measure_frequency_unit == 'shift' and (diff >= result.measure_frequency_unit_value * 8):
            return True
        elif result.measure_frequency_unit == 'day' and (diff >= result.measure_frequency_unit_value * 24):
            return True
        elif result.measure_frequency_unit == 'week' and (diff >= result.measure_frequency_unit_value * 24 * 7):
            return True
        elif result.measure_frequency_unit == 'month' and (diff >= result.measure_frequency_unit_value * 24 * 30):
            return True
        elif result.measure_frequency_type == 'all':
            return True
        else:
            return False

    def corn_create_check_point(self):
        for rec in self.env['quality.point'].search([('auto_check_point', '=', True)]):
            print('----->', rec.name, fields.Datetime.now(), rec.next_create_time, rec.last_create_time)
            if rec.next_create_time:
                diff = fields.Datetime.now() - rec.next_create_time
                if rec.last_create_time:
                    diff2 = fields.Datetime.now() - rec.last_create_time
                    print(';;;;;;', diff2.total_seconds() / 60)
                    create_new = self.if_create_new(diff2.total_seconds() / 60, rec)
                else:
                    create_new = True
                diff = diff.total_seconds() / 60
                print('---->', diff)
                if create_new and diff >= 0:
                    # if diff >=0  and diff :
                    print('jjj', rec.auto_check_point, rec.next_create_time)
                    check_point = self.env['quality.check'].create({
                        'point_id': rec.id,
                        'test_type_id': rec.test_type_id.id,
                        'team_id': rec.team_id.id,
                        'company_id': rec.company_id.id,
                    })
                    self.set_next_create_time(rec)
                    rec.last_create_time = fields.Datetime.now()
                    print('j222jj', check_point.name, rec.many_user_id)
                    if rec.many_user_id:
                        for user in rec.many_user_id:
                            notification_ids = [((0, 0, {
                                'res_partner_id': user.partner_id.id,
                                'notification_type': 'inbox'}))]
                            print('-->2', notification_ids)
                            message = ("A check Point Just Created %s") % (check_point.name)

                            check_point.message_post(body=(message),
                                                     message_type='notification',
                                                     subtype_xmlid="mail.mt_comment",
                                                     notification_ids=notification_ids,
                                                     # notified_partner_ids=[user.partner_id.id],
                                                     notify_by_email=False,
                                                     )
                            notification_ids = []

    def create_check_point_for_p_days(self):
        for rec in self.env['quality.point'].search([('auto_check_point_day', '=', True)]):
            week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            # date = datetime.strptime(str(datetime.today()), "%m/%d/%Y")
            today_name = week[datetime.today().weekday()]
            #             check if today in p_days or not and take action
            for d in rec.days_ids:
                print('in for loop .......', d.name, today_name)
                if d.name.upper() == today_name.upper():
                    check_point = self.env['quality.check'].create({
                        'point_id': rec.id,
                        'test_type_id': rec.test_type_id.id,
                        'team_id': rec.team_id.id,
                        'company_id': rec.company_id.id,
                    })
                    print('j222jj', check_point.name, rec.many_user_id)
                    message = ("A check Point Just Created %s") % (check_point.name)
                    if rec.many_user_id:
                        for user in rec.many_user_id:
                            notification_ids = [((0, 0, {
                                'res_partner_id': user.partner_id.id,
                                'notification_type': 'inbox'}))]
                            print('-->2', notification_ids, user.partner_id.id)
                            check_point.message_post(body=(message),
                                                     message_type='notification',
                                                     subtype_xmlid="mail.mt_comment",
                                                     notification_ids=notification_ids,
                                                     # notified_partner_ids=[user.partner_id.id],
                                                     notify_by_email=False,
                                                     )
                            notification_ids = []
                            print('notification', notification_ids)


class checks(models.Model):
    _inherit = 'quality.check'
    branch_id = fields.Many2one(related="point_id.branch_id", string="Branches", store=True)
    quality_type_id = fields.Many2one(related="point_id.quality_type_id", string="Quality Type", store=True)
    division_ids = fields.Many2many('division', string="Divisions", compute="get_diviion_points", store=True)
    reason = fields.Char()
    tags = fields.Many2many('quality.tag', String='Tags', compute="get_diviion_points", store=True)
    move_raw_ids = fields.One2many(
        'stock.move', 'check_id', 'Components_check',
        store=True, readonly=False,
        copy=False,)
    qty = fields.Float('Product Quantity')

    @api.depends('point_id')
    def get_diviion_points(self):
        for rec in self:
            rec.division_ids = rec.tags = []
            division_ids = tags = []
            if rec.point_id:
                for point in rec.point_id:
                    rec.division_ids = point.division_ids
                    rec.tags = point.tags

    def do_alert(self):
        res = super(checks, self).do_alert()
        print('oooooooooooooooooooooooooooooooo')
        if self.point_id.many_user_id:
            message = ("an alert from check Point number  %s") % (self.name)
            for user in self.point_id.many_user_id:
                notification_ids = [((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox',
                    'is_read': False
                }))]
                print('-rrr->2', notification_ids, user.partner_id.id)
                self.message_post(body=(message),
                                  message_type='notification',
                                  subtype_xmlid="mail.mt_comment",
                                  notification_ids=notification_ids,
                                  # notified_partner_ids=[user.partner_id.id],
                                  notify_by_email=False,
                                  )
                notification_ids = []
                print('notification', notification_ids)

    def create_checks_related(self, control):
        check_point = self.env['quality.check'].create({
            'point_id': control.id,
            'test_type_id': control.test_type_id.id,
            'team_id': control.team_id.id,
            'company_id': control.company_id.id,
        })
        if control.many_user_id:
            message = ("A check Point Just Created %s") % (check_point.name)
            for user in control.many_user_id:
                notification_ids = [((0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'}))]
                print('-->2', notification_ids, user.partner_id.id)
                check_point.message_post(body=(message),
                                         message_type='notification',
                                         subtype_xmlid="mail.mt_comment",
                                         notification_ids=notification_ids,
                                         # notified_partner_ids=[user.partner_id.id],
                                         notify_by_email=False,
                                         )
                notification_ids = []
                print('notification', notification_ids)

    def do_pass(self):
        res = super(checks, self).do_pass()
        print('[[[[[[[[[[[[[[[[[[[[[', self.company_id.add_related_control_point)
        if self.company_id.add_related_control_point:
            if self.point_id.product_ids or self.point_id.picking_type_ids:
                for i in self.point_id.quality_control_related_ids:
                    print('create check points', i.name)
                    self.create_checks_related(i)
        return res

    def fail_reason(self):
        view_form = self.env.ref('dan_adj.qualti_reason_fial_view_form')

        return {
            'name': _('Fail Reason'),
            'view_mode': 'form',

            'views': [(view_form.id, 'form')],
            'res_model': 'quality.check',
            'type': 'ir.actions.act_window',
            'res_id':self.id,
            'target': 'new'
        }

    # todo boolean in config to make a task related
    def do_fail(self):
        res = super(checks, self).do_fail()
        if self.company_id.add_related_control_point:
            if self.point_id.product_ids or self.point_id.picking_type_ids:
                for i in self.point_id.quality_control_related_ids:
                    self.create_checks_related(i)
            message = ("A check Point Just failed %s") % (self.name)
            for i in self.point_id.fail_many_user_id:
                notification_ids = [((0, 0, {
                    'res_partner_id': i.partner_id.id,
                    'notification_type': 'inbox',
                    'is_read': False}))]
                self.message_post(body=(message),
                                  message_type='notification',
                                  subtype_xmlid="mail.mt_comment",
                                  notification_ids=notification_ids,
                                  # notified_partner_ids=[i.partner_id.id],
                                  notify_by_email=False,
                                  )
                notification_ids = []

        return res

    def do_fail_open_alert(self):
        print('llllllllllllllllllll')
        self.do_fail()
        print('llllllllllrrrrrrrrllllllllll')
        alert = self.env['quality.alert'].create({
            'check_id':self.id,
            'reason':self.reason,
            'team_id':self.team_id.id,
            'title':self.x_title,
            'description':self.note,
            'branch_id':self.branch_id.id if self.branch_id else False,
            'product_id':self.product_id.id if self.product_id else False,
        })
        return {
            'name': _('Quality Alert'),
            'type': 'ir.actions.act_window',
            'res_model': 'quality.alert',
            'views': [(self.env.ref('quality_control.quality_alert_view_form').id, 'form')],
            'res_id': alert.id,
        }


class Company(models.Model):
    _inherit = "res.company"

    add_related_control_point = fields.Boolean('Add Related Control Points')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    add_related_control_point = fields.Boolean('Add Related Control Points',
                                               related='company_id.add_related_control_point', readonly=False)
