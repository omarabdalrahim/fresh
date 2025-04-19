
import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request
from datetime import datetime

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
# omar
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from dateutil.relativedelta import relativedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta

class SaleCustom(WebsiteSale):

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        print('odoo----------------')

        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        redirection = self.checkout_check_address(order)
        if redirection:
            return redirection

        values = self.checkout_values(**post)
        allowed_days = True
        if order.partner_id.x_days_deliver_ids:
            allowed_days=False

        if post.get('delivery_date'):
            print('odoo---------------in-')
            week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            date = datetime.strptime(post['delivery_date'], "%m/%d/%Y")
            day = week[date.weekday()]
            allowed_days = False
            print("--===", day, allowed_days)
            for d in order.partner_id.x_days_deliver_ids:
                if d.x_name == day:
                    allowed_days = True

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        if allowed_days:
            print('odoo---------------in-1')
            values.update({'website_sale_order': order, 'pay_now_div': 1})
        else:
            print('odoo---------------in-(-1)')
            values.update({'website_sale_order': order, 'pay_now_div': -1})
        if not post.get('delivery_date'):
            print('odoo---------------in-0')
            values.update({'website_sale_order': order, 'pay_now_div':0})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)


    # @http.route(['/shop/payment/deliverydate'], type='http', auth="public", website=True, sitemap=False)
    # def delivery_date(self, **post):
    #     print('odoo----------website------',post)
    #     order = request.website.sale_get_order()
    #     # values = self.checkout_values(**post)
    #     print('->',order.partner_id,order.partner_id.delivery_days)
    #     # check date days
    #     week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    #     date = datetime.strptime(post['delivery_date'], "%d-%m-%Y")
    #     day=week[date.weekday()]
    #     allowed_days= False
    #     print("--===", day, allowed_days)
    #     for d in order.partner_id.delivery_days:
    #         if d.name == day:
    #             allowed_days=True
    #
    #
    #     render_values = self._get_shop_payment_values(order, **post)
    #     render_values['only_services'] = order and order.only_services or False
    #
    #     if allowed_days:
    #         render_values.update({'website_sale_order': order, 'pay_now_div': 1})
    #     else:
    #         render_values.update({'website_sale_order': order, 'pay_now_div': -1})
    #
    #     if render_values['errors']:
    #         render_values.pop('acquirers', '')
    #         render_values.pop('tokens', '')
    #
    #     return request.render("website_sale.payment", render_values)


    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        print('heeere ---> payment')
        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection
        str_days = ''
        allowed_days = False

        if post.get('delivery_date'):
            print('odoo---------------in-')
            week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            date = datetime.strptime(post['delivery_date'], "%m/%d/%Y")
            print("=====================",(date-datetime.today()).days,order.partner_id.x_before_delivery)
            if (date-datetime.today() ).days+1<=order.partner_id.x_before_delivery:
                allowed_days = False
                str_days += ' يمكن انشاء بعد %s من تاريخ اليوم'%str(order.partner_id.x_before_delivery)
            else:

                day = week[date.weekday()]
                print("--===", day, allowed_days)
                for d in order.partner_id.x_days_deliver_ids:
                    str_days +=d.x_name+' '
                    print('---',str_days)
                    if d.x_name.lower() == day.lower():
                        allowed_days = True
                if not order.partner_id.x_days_deliver_ids or allowed_days==True:
                    order.customer_order_delivery_date = date
                    order.x_customer_order_delivery_date = date
                    if post.get('delivery_comment'):
                        order.customer_order_delivery_comment = post['delivery_comment']
                    if not order.partner_id.x_days_deliver_ids:
                        allowed_days=True




        render_values = self._get_shop_payment_values(order, **post)
        # print('methods', render_values['tokens'], render_values['acquirers'])
        render_values['only_services'] = order and order.only_services or False
        if post.get('delivery_date'):
            if allowed_days:
                print('odoo---------------in-1')
                render_values.update({ 'pay_now_div': 1})
            else :
                print('odoo---------------in-(-1)')
                render_values.update({ 'pay_now_div': 0,'error_date':1,'days':str_days})
        if not post.get('delivery_date'):
            print('odoo---------------in-0')
            render_values.update({ 'pay_now_div': 0,'error_date':0})

        if render_values['errors']:
            render_values.pop('providers', '')
            render_values.pop('tokens', '')


        return request.render("website_sale.payment", render_values)
