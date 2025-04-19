from odoo import fields, models, api

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
# omar
# from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website.models import ir_http
from odoo.tools.translate import html_translate
from odoo.osv import expression

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"
    def _check_website_pricelist(self):
        return True
        # for website in self.env['website'].search([]):
        #     if not website.pricelist_ids:

                # raise UserError(
                #     _("With this action, '%s' website would not have any pricelist available.") % (website.name))
