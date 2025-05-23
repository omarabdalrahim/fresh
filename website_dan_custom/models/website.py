# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import logging

from odoo import api, fields, models, tools, SUPERUSER_ID, _

from odoo.http import request
from odoo.addons.website.models import ir_http
from odoo.addons.http_routing.models.ir_http import url_for

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


_logger = logging.getLogger(__name__)
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager

class Website(models.Model):
    _inherit = 'website'

    # def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
    #     """ Return the current sales order after mofications specified by params.
    #     :param bool force_create: Create sales order if not already existing
    #     :param str code: Code to force a pricelist (promo code)
    #                      If empty, it's a special case to reset the pricelist with the first available else the default.
    #     :param bool update_pricelist: Force to recompute all the lines from sales order to adapt the price with the current pricelist.
    #     :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
    #     :returns: browse record for the current sales order
    #     """
    #     self.ensure_one()
    #     partner = self.env.user.partner_id
    #     sale_order_id = request.session.get('sale_order_id')
    #
    #     check_fpos = False
    #     print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.",sale_order_id,force_create)
    #     if not sale_order_id and not self.env.user._is_public():
    #         last_order = partner.last_website_so_id
    #         print("============",last_order)
    #         if last_order:
    #             available_pricelists = self.get_pricelist_available()
    #             # Do not reload the cart of this user last visit if the cart uses a pricelist no longer available.
    #             sale_order_id = last_order.pricelist_id in available_pricelists and last_order.id
    #             check_fpos = True
    #
    #     # Test validity of the sale_order_id
    #     sale_order = self.env['sale.order'].with_company(request.website.company_id.id).sudo().browse(sale_order_id).exists() if sale_order_id else None
    #     print("+++++++",sale_order)
    #
    #
    #     # Do not reload the cart of this user last visit if the Fiscal Position has changed.
    #     if check_fpos and sale_order:
    #         fpos_id = (
    #             self.env['account.fiscal.position'].sudo()
    #             .with_company(sale_order.company_id.id)
    #             .get_fiscal_position(sale_order.partner_id.id, delivery_id=sale_order.partner_shipping_id.id)
    #         ).id
    #         if sale_order.fiscal_position_id.id != fpos_id:
    #             sale_order = None
    #
    #     if not (sale_order or force_create or code):
    #         if request.session.get('sale_order_id'):
    #             request.session['sale_order_id'] = None
    #         return self.env['sale.order']
    #
    #     if self.env['product.pricelist'].browse(force_pricelist).exists():
    #         pricelist_id = force_pricelist
    #         request.session['website_sale_current_pl'] = pricelist_id
    #         update_pricelist = True
    #     else:
    #         pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id
    #
    #     if not self._context.get('pricelist'):
    #         self = self.with_context(pricelist=pricelist_id)
    #
    #     # cart creation was requested (either explicitly or to configure a promo code)
    #     if not sale_order:
    #         # TODO cache partner_id session
    #         pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
    #         so_data = self._prepare_sale_order_values(partner, pricelist)
    #         sale_order = self.env['sale.order'].with_company(request.website.company_id.id).with_user(SUPERUSER_ID).create(so_data)
    #
    #         # set fiscal position
    #         if request.website.partner_id.id != partner.id:
    #             sale_order.onchange_partner_shipping_id()
    #         else: # For public user, fiscal position based on geolocation
    #             country_code = request.session['geoip'].get('country_code')
    #             if country_code:
    #                 country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
    #                 sale_order.fiscal_position_id = request.env['account.fiscal.position'].sudo().with_company(request.website.company_id.id)._get_fpos_by_region(country_id)
    #             else:
    #                 # if no geolocation, use the public user fp
    #                 sale_order.onchange_partner_shipping_id()
    #
    #         request.session['sale_order_id'] = sale_order.id
    #
    #         # The order was created with SUPERUSER_ID, revert back to request user.
    #         sale_order = sale_order.with_user(self.env.user).sudo()
    #
    #     # case when user emptied the cart
    #     if not request.session.get('sale_order_id'):
    #         request.session['sale_order_id'] = sale_order.id
    #
    #     # check for change of pricelist with a coupon
    #     pricelist_id = pricelist_id or partner.property_product_pricelist.id
    #
    #     # check for change of partner_id ie after signup
    #     if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
    #         flag_pricelist = False
    #         if pricelist_id != sale_order.pricelist_id.id:
    #             flag_pricelist = True
    #         fiscal_position = sale_order.fiscal_position_id.id
    #
    #         # change the partner, and trigger the onchange
    #         sale_order.write({'partner_id': partner.id})
    #         sale_order.with_context(not_self_saleperson=True).onchange_partner_id()
    #         sale_order.write({'partner_invoice_id': partner.id})
    #         sale_order.onchange_partner_shipping_id() # fiscal position
    #         sale_order['payment_term_id'] = self.sale_get_payment_term(partner)
    #
    #         # check the pricelist : update it if the pricelist is not the 'forced' one
    #         values = {}
    #         if sale_order.pricelist_id:
    #             if sale_order.pricelist_id.id != pricelist_id:
    #                 values['pricelist_id'] = pricelist_id
    #                 update_pricelist = True
    #
    #         # if fiscal position, update the order lines taxes
    #         if sale_order.fiscal_position_id:
    #             sale_order._compute_tax_id()
    #
    #         # if values, then make the SO update
    #         if values:
    #             sale_order.write(values)
    #
    #         # check if the fiscal position has changed with the partner_id update
    #         recent_fiscal_position = sale_order.fiscal_position_id.id
    #         # when buying a free product with public user and trying to log in, SO state is not draft
    #         if (flag_pricelist or recent_fiscal_position != fiscal_position) and sale_order.state == 'draft':
    #             update_pricelist = True
    #
    #     if code and code != sale_order.pricelist_id.code:
    #         code_pricelist = self.env['product.pricelist'].sudo().search([('code', '=', code)], limit=1)
    #         if code_pricelist:
    #             pricelist_id = code_pricelist.id
    #             update_pricelist = True
    #     elif code is not None and sale_order.pricelist_id.code and code != sale_order.pricelist_id.code:
    #         # code is not None when user removes code and click on "Apply"
    #         pricelist_id = partner.property_product_pricelist.id
    #         update_pricelist = True
    #
    #     # update the pricelist
    #     if update_pricelist:
    #         request.session['website_sale_current_pl'] = pricelist_id
    #         values = {'pricelist_id': pricelist_id}
    #         sale_order.write(values)
    #         for line in sale_order.order_line:
    #             if line.exists():
    #                 sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
    #
    #     return sale_order
    def _get_current_pricelist_id(self, partner_sudo):
        if partner_sudo.property_product_pricelist:
            return partner_sudo.property_product_pricelist.id
        else:
            return self.get_current_pricelist().id

        # return self.get_current_pricelist().id \
        #     or partner_sudo.property_product_pricelist.id
