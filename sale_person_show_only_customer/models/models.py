# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_show = fields.Boolean()

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if self.env.user.has_group('sale_person_show_only_customer.show_only_customer'):
            domain += [('user_id', '=', self.env.user.id)]

        return super(ResPartner, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_idl_id(self):
        if self.env.user.has_group(
                'sale_person_show_only_customer.show_only_customer'):
            domain = []
            domain.append(('user_id', '=', self.env.uid))

            return {
                'domain': {'partner_id': domain}}
