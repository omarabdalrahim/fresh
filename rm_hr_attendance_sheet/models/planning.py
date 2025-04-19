from odoo import fields, models, api
from dateutil import relativedelta
import pytz
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from odoo import models, fields, tools, api, exceptions, _


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"

class Planning(models.Model):
    _inherit = "planning.slot"
    date = fields.Date(compute='get_date_start',store=True)

    @api.depends('start_datetime')
    def get_date_start(self):
        for rec in self:
            rec.date =''
            if rec.start_datetime:


                rec.date = (pytz.utc.localize(rec.start_datetime).astimezone(pytz.timezone(rec.employee_id.tz))).date()