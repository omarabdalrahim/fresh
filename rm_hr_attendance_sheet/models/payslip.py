import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date


class Payslip(models.Model):
    _inherit = "hr.payslip"

    def compute_sheet(self):
        for rec in self:

            sheet_id = self.env['attendance.sheet'].search(
                [('employee_id', '=', rec.employee_id.id), ('date_from', '=', rec.date_from),
                 ('date_to', '=', rec.date_to),('state','=','done')], limit=1)
            for ll in rec.worked_days_line_ids:
                if ll.code in ('OVT', 'ATTSHDT', 'ATTSHAB', 'ATTSHOT','ATTSHLI'):
                    ll.unlink()
            self.contract_id.resource_calendar_id.hours_per_day if self.contract_id.resource_calendar_id.hours_per_day > 0 else 0,
            if sheet_id:
                sheet_id.action_create_payslip_from_payslip(rec)
                for ll in rec.worked_days_line_ids:
                    if  rec.contract_id.resource_calendar_id.hours_per_day>0 and ll.code in ('OVT', 'ATTSHDT', 'ATTSHAB', 'ATTSHOT','ATTSHLI'):
                        ll.number_of_days = ll.number_of_hours/rec.contract_id.resource_calendar_id.hours_per_day


        res = super(Payslip,self).compute_sheet()

        return res

    # @api.model
    # def create(self, vals):
    #     res = super(Payslip, self).create(vals)
    #     for rec in self:
    #         print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    #         sheet_id = self.env['attendance.sheet'].search(
    #             [('employee_id', '=', rec.employee_id.id), ('date_from', '=', rec.date_from),
    #              ('date_to', '=', rec.date_to),('state','=','done')], limit=1)
    #         print("==============",sheet_id)
    #         if sheet_id:
    #             sheet_id.action_create_payslip_from_payslip()
    #     return res
