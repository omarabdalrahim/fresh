from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Company(models.Model):
    _inherit = "res.company"

    ks_remove_tax = fields.Boolean( string="Remove Default Tax ")
class order(models.Model):
    _inherit='sale.order'

    default_remove_tax = fields.Boolean(compute='get_default_remove_tax')
    remove_tax = fields.Boolean("Remove Tax")

    # @api.onchange("remove_tax", "order_line")
    # def _remove_taxes(self):
    #     print("/////",self.remove_tax)
    #     for rec in self.order_line:
    #         if self.remove_tax == True:
    #             rec.tax_id = [(5,)]
    #         if self.remove_tax == False:
    #             if self.company_id.account_sale_tax_id:
    #                  rec.tax_id = [(4, self.company_id.account_sale_tax_id.id)]
    @api.depends("company_id")
    def get_default_remove_tax(self):


        for rec in self:

            if rec.company_id.ks_remove_tax==True:
                rec.default_remove_tax = True
                rec.remove_tax=True
            else:
                rec.default_remove_tax = False




    # @api.model
    # def create(self,vals):
    #     if 'default_remove_tax' in vals:
    #         print(">>>>>>>>>>>>>>>>")
    #
    #     return super(order, self).create(vals)
class KSResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    ks_remove_tax = fields.Boolean(string="Remove Default Tax ",related='company_id.ks_remove_tax', readonly=False)
