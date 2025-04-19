
import binascii

from odoo import fields, http, SUPERUSER_ID, _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request

from odoo.addons.payment.controllers import portal as payment_portal
from odoo.addons.payment import utils as payment_utils
# omar
# from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager
from dateutil.relativedelta import relativedelta
from datetime import datetime
class CustomerPortal(portal.CustomerPortal):
    def _prepare_orders_domain(self, partner):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",\
              partner,datetime.today()-relativedelta(months=1))
        return [
            ('date_order','>=',datetime.today()-relativedelta(months=1)),
            ('date_order','<=',datetime.today()),
            ('partner_id', '=', partner.id),
            ('state', 'in', ['sale', 'done'])
        ]

