# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)
class Product(models.Model):
    _inherit = 'product.product'


    @api.model
    def create(self,vals):
        res=super(Product, self).create(vals)
        if not self.env.user.has_group('access_right_product_contact.group_create_product'):
            raise ValidationError("You Cann't Create Product return to admin")
        return res
class Conatct(models.Model):
    _inherit = 'res.partner'


    @api.model
    def create(self,vals):
        res=super(Conatct, self).create(vals)
        _logger.info("===============")
        _logger.info(self.env.user)

        if not self.env.user.has_group('access_right_product_contact.group_create_contact_2') and \
                not self.env.user.has_group('base.group_public') :
            raise ValidationError("You Cann't Create Contact return to admin")
        return res
