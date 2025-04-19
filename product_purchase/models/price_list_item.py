from odoo import models, fields, api, _,tools

from odoo.tools import float_repr
import  math
from odoo.exceptions import UserError, ValidationError
from itertools import chain
class pricelist(models.Model):
    _inherit = 'product.pricelist'
    discount = fields.Float("Discount")





class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'
    puchase_price= fields.Float("Price of Purchase ",store=False,compute='_get_last_purchase_price')
    amount_list= fields.Selection([('Precentage','Precentage'),('Amount','Amount')],'Type')
    amount= fields.Float("Amount")
    precentage= fields.Float("Precentage")
    update_price = fields.Float("Update Purchase price")



    compute_price = fields.Selection([
        ('fixed', 'Fixed Price'),
        ('percentage', 'Percentage (discount)'),
        ('formula', 'Formula'),('Purchase Price', 'Purchase Price')], index=True, default='fixed', required=True)
    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}
    def update_purchase_order(self):
        view = self.env.ref('product_purchase.update_pricelist_purchase_price')
        print("Id",self.id)
        print({'default_res_id':self.id})
        return {
            'name': _('Update Purchase Price'),
            'view_type': 'form',
            "view_mode": 'form',
            'view_id': view.id,
            'res_model': 'product.pricelist.item',
            'type': 'ir.actions.act_window',
             'res_id': self.id,
            'target': 'new'
        }

    @api.depends('product_tmpl_id','update_price')
    def _get_last_purchase_price(self):

        for rec in self:
            bom=[]
            rec.puchase_price = 0
            if rec.update_price !=0:
                rec.puchase_price=rec.update_price
                return 
            if rec.product_id:
                bom = self.env['mrp.bom'].search([('product_id', '=', rec.product_id.id)], order='write_date desc',
                                                 limit=1)

            elif rec.product_tmpl_id:
               bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', rec.product_tmpl_id.id)] ,order='write_date desc', limit=1)
            if bom :
                pur_price=0
                for record in bom.bom_line_ids:
                    po = self.env['purchase.order.line'].search(
                        [('state', '=', 'purchase'),('partner_id','=',2908),('product_id', '=', record.product_id.id)],
                        order='write_date desc', limit=1)
                    print(po)
                    pur_price += (po.price_unit * record.product_qty)

                if pur_price > 0 and rec.update_price ==0:
                    rec.puchase_price = pur_price
                    return

            
            if rec.product_tmpl_id:
                purchase_order_line = rec.env['purchase.order.line'].search([('partner_id','=',2908),('state','=','purchase'),('product_id.product_tmpl_id','=',rec.product_tmpl_id.id)],order ='write_date desc')

                if purchase_order_line:

                   rec.puchase_price=purchase_order_line[0].price_unit
                else:
                    rec.puchase_price = 0
            elif rec.product_id:
                purchase_order_line = rec.env['purchase.order.line'].search([('partner_id','=',2908),('state','=','purchase'),('product_id','=',rec.product_id.id)],order ='write_date desc')

                if purchase_order_line:

                   rec.puchase_price=purchase_order_line[0].price_unit
                else:
                    rec.puchase_price = 0




    # @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
    #              'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge',"amount_list","precentage","amount")
    # def _get_pricelist_item_name_price(self):
    #     for item in self:
    #         if item.categ_id and item.applied_on == '2_product_category':
    #             item.name = _("Category: %s") % (item.categ_id.display_name)
    #         elif item.product_tmpl_id and item.applied_on == '1_product':
    #             item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
    #         elif item.product_id and item.applied_on == '0_product_variant':
    #             item.name = _("Variant: %s") % (item.product_id.with_context(display_default_code=False).display_name)
    #         else:
    #             item.name = _("All Products")
    #
    #         if item.compute_price == 'fixed':
    #             decimal_places = self.env['decimal.precision'].precision_get('Product Price')
    #             # fixed =  rec.fixed_price - (rec.fixed_price * (rec.pricelist_id.discount / 100))
    #             fixed = item.fixed_price
    #             if item.pricelist_id.discount>0:
    #
    #                 fixed = fixed - (fixed * (item.pricelist_id.discount / 100))
    #
    #
    #
    #             if item.currency_id.position == 'after':
    #                 item.price = "%s %s" % (
    #                     float_repr(
    #                         fixed,
    #                         decimal_places,
    #                     ),
    #                     item.currency_id.symbol,
    #                 )
    #             else:
    #                 item.price = "%s %s" % (
    #                     item.currency_id.symbol,
    #                     float_repr(
    #                         fixed,
    #                         decimal_places,
    #                     ),
    #                 )
    #         elif item.compute_price == 'percentage':
    #             percentage = item.percent_price
    #             if item.pricelist_id.discount >0:
    #                 percentage = item.pricelist_id.discount
    #
    #
    #             item.price = _("%s %% discount") % (item.percent_price)
    #         elif item.amount_list=='Precentage':
    #             purchase = item.puchase_price
    #
    #             x = ((purchase*item.precentage)/100)+purchase
    #             if item.pricelist_id.discount > 0:
    #                 x = x - (x * (item.pricelist_id.discount / 100))
    #             y = x - math.floor(x)
    #             y = round(y, 2)
    #
    #             print(y)
    #             if y>0 and y < 0.25:
    #                 y = 0.25
    #             elif y > 0.25 and y <= 0.5:
    #                 y = 0.5
    #             elif y > 0.5 and y <= 0.75:
    #                 y = 0.75
    #             elif y>0.75:
    #                 y = 1
    #             decimal_places = self.env['decimal.precision'].precision_get('Product Price')
    #             item.price =math.floor(x) + y
    #
    #
    #
    #
    #         elif  item.amount_list=='Amount':
    #
    #             x=item.puchase_price + item.amount
    #             if item.pricelist_id.discount > 0:
    #                 x = x - (x * (item.pricelist_id.discount / 100))
    #             y = x - math.floor(x)
    #             y = round(y, 2)
    #
    #             print(y)
    #             if y>0 and y < 0.25:
    #                 y = 0.25
    #             elif y > 0.25 and y <= 0.5:
    #                 y = 0.5
    #             elif y > 0.5 and y <= 0.75:
    #                 y = 0.75
    #             elif y > 0.75:
    #                 y = 1
    #             decimal_places = self.env['decimal.precision'].precision_get('Product Price')
    #             item.price =math.floor(x) + y
    #
    #
    #
    #
    #         else:
    #             item.price = _("%s %% discount and %s surcharge") % (item.price_discount, item.price_surcharge)



class PriceList(models.Model):
    _inherit = 'product.pricelist'
    # def _compute_price_rule(self, products_qty_partner, date=False, uom_id=False):
    #     print("get_products_price")
    #     """ Low-level method - Mono pricelist, multi products
    #     Returns: dict{product_id: (price, suitable_rule) for the given pricelist}
    #
    #     Date in context can be a date, datetime, ...
    #
    #         :param products_qty_partner: list of typles products, quantity, partner
    #         :param datetime date: validity date
    #         :param ID uom_id: intermediate unit of measure
    #     """
    #     self.ensure_one()
    #     if not date:
    #         date = self._context.get('date') or fields.Date.today()
    #     date = fields.Date.to_date(date)  # boundary conditions differ if we have a datetime
    #     if not uom_id and self._context.get('uom'):
    #         uom_id = self._context['uom']
    #     if uom_id:
    #         # rebrowse with uom if given
    #         products = [item[0].with_context(uom=uom_id) for item in products_qty_partner]
    #         products_qty_partner = [(products[index], data_struct[1], data_struct[2]) for index, data_struct in
    #                                 enumerate(products_qty_partner)]
    #     else:
    #         products = [item[0] for item in products_qty_partner]
    #
    #     if not products:
    #         return {}
    #
    #     categ_ids = {}
    #     for p in products:
    #         categ = p.categ_id
    #         while categ:
    #             categ_ids[categ.id] = True
    #             categ = categ.parent_id
    #     categ_ids = list(categ_ids)
    #
    #     is_product_template = products[0]._name == "product.template"
    #     if is_product_template:
    #         prod_tmpl_ids = [tmpl.id for tmpl in products]
    #         # all variants of all products
    #         prod_ids = [p.id for p in
    #                     list(chain.from_iterable([t.product_variant_ids for t in products]))]
    #     else:
    #         prod_ids = [product.id for product in products]
    #         prod_tmpl_ids = [product.product_tmpl_id.id for product in products]
    #
    #     items = self._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids,
    #                                                categ_ids)
    #
    #     results = {}
    #     for product, qty, partner in products_qty_partner:
    #         results[product.id] = 0.0
    #         suitable_rule = False
    #
    #         # Final unit price is computed according to `qty` in the `qty_uom_id` UoM.
    #         # An intermediary unit price may be computed according to a different UoM, in
    #         # which case the price_uom_id contains that UoM.
    #         # The final price will be converted to match `qty_uom_id`.
    #         qty_uom_id = self._context.get('uom') or product.uom_id.id
    #         price_uom_id = product.uom_id.id
    #         qty_in_product_uom = qty
    #         if qty_uom_id != product.uom_id.id:
    #             try:
    #                 qty_in_product_uom = self.env['uom.uom'].browse([self._context['uom']])._compute_quantity(qty,
    #                                                                                                           product.uom_id)
    #             except UserError:
    #                 # Ignored - incompatible UoM in context, use default product UoM
    #                 pass
    #
    #         # if Public user try to access standard price from website sale, need to call price_compute.
    #         # TDE SURPRISE: product can actually be a template
    #         price = product.price_compute('list_price')[product.id]
    #
    #         price_uom = self.env['uom.uom'].browse([qty_uom_id])
    #         for rule in items:
    #             if rule.min_quantity and qty_in_product_uom < rule.min_quantity:
    #                 continue
    #             if is_product_template:
    #                 if rule.product_tmpl_id and product.id != rule.product_tmpl_id.id:
    #                     continue
    #                 if rule.product_id and not (
    #                         product.product_variant_count == 1 and product.product_variant_id.id == rule.product_id.id):
    #                     # product rule acceptable on template if has only one variant
    #                     continue
    #             else:
    #                 if rule.product_tmpl_id and product.product_tmpl_id.id != rule.product_tmpl_id.id:
    #                     continue
    #                 if rule.product_id and product.id != rule.product_id.id:
    #                     continue
    #
    #             if rule.categ_id:
    #                 cat = product.categ_id
    #                 while cat:
    #                     if cat.id == rule.categ_id.id:
    #                         break
    #                     cat = cat.parent_id
    #                 if not cat:
    #                     continue
    #
    #             if rule.base == 'pricelist' and rule.base_pricelist_id:
    #                 price_tmp = \
    #                 rule.base_pricelist_id._compute_price_rule([(product, qty, partner)], date, uom_id)[product.id][
    #                     0]  # TDE: 0 = price, 1 = rule
    #                 price = rule.base_pricelist_id.currency_id._convert(price_tmp, self.currency_id, self.env.company,
    #                                                                     date, round=False)
    #             else:
    #                 # if base option is public price take sale price else cost price of product
    #                 # price_compute returns the price in the context UoM, i.e. qty_uom_id
    #                 price = product.price_compute(rule.base)[product.id]
    #
    #             convert_to_price_uom = (lambda price: product.uom_id._compute_price(price, price_uom))
    #
    #             if price is not False:
    #                 if rule.compute_price == 'fixed':
    #                     price = convert_to_price_uom(rule.fixed_price)
    #                 elif rule.compute_price == 'percentage':
    #                     price = (price - (price * (rule.percent_price / 100))) or 0.0
    #                 elif rule.compute_price == 'Purchase Price':
    #                     price = rule.price
    #                     print("purchase price ",price)
    #
    #                 else:
    #                     # complete formula
    #                     price_limit = price
    #                     price = (price - (price * (rule.price_discount / 100))) or 0.0
    #                     if rule.price_round:
    #                         price = tools.float_round(price, precision_rounding=rule.price_round)
    #
    #                     if rule.price_surcharge:
    #                         price_surcharge = convert_to_price_uom(rule.price_surcharge)
    #                         price += price_surcharge
    #
    #                     if rule.price_min_margin:
    #                         price_min_margin = convert_to_price_uom(rule.price_min_margin)
    #                         price = max(price, price_limit + price_min_margin)
    #
    #                     if rule.price_max_margin:
    #                         price_max_margin = convert_to_price_uom(rule.price_max_margin)
    #                         price = min(price, price_limit + price_max_margin)
    #                 suitable_rule = rule
    #
    #             break
    #         # Final price conversion into pricelist currency
    #         if suitable_rule and suitable_rule.compute_price != 'fixed' and suitable_rule.base != 'pricelist':
    #             if suitable_rule.base == 'standard_price':
    #                 cur = product.cost_currency_id
    #             else:
    #                 cur = product.currency_id
    #             price = cur._convert(price, self.currency_id, self.env.company, date, round=False)
    #
    #         if not suitable_rule:
    #             cur = product.currency_id
    #             price = cur._convert(price, self.currency_id, self.env.company, date, round=False)
    #
    #         results[product.id] = (price, suitable_rule and suitable_rule.id or False)
    #
    #     return results

