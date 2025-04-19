# -*- coding: utf-8 -*-

from odoo import models, fields, api

# Timedelta function demonstration

from datetime import datetime, timedelta

from odoo.exceptions import UserError, AccessError, ValidationError

class Partner(models.Model):
    _inherit = "res.partner"
    @api.constrains('x_before_delivery')
    def check_x_before_delivery(self):
        if self.x_before_delivery<0:
            raise ValidationError("لم يمكن الحذف قيمه سالبها")
class delivery_date_days(models.Model):
    _inherit = 'sale.order'
    @api.constrains('x_customer_order_delivery_date')
    def check_x_customer_order_delivery_date(self):

        for line in self:
            if line.partner_id.x_days_deliver_ids:
                list=[]
                names=''
                for rec in line.partner_id.x_days_deliver_ids:
                    list.append(rec.x_code)
                    names+=rec.x_name+"-"
                if not self.env.user.has_group('delivery_date_days.group_change_delivery_date'):
                    if line.x_customer_order_delivery_date :
                        if  line.x_customer_order_delivery_date.weekday()+1 not in list:
                            raise ValidationError("من فضللك يمكن طلب امر البيع ف الايام المحدد لك %s"%(names))
                    if line.partner_id.x_before_delivery:
                        if line.x_customer_order_delivery_date-timedelta(days=line.partner_id.x_before_delivery) < datetime.today().date():
                            raise ValidationError("من فضللك طلب الاورد ف الايام المحدده قبل يوم الطلب ب %s"%(line.partner_id.x_before_delivery))