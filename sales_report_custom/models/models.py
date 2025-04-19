# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SAeOrder(models.Model):
    _inherit = 'account.move'
    x_customer_order_delivery_date = fields.Date(compute='get_delivery_date',store=True,index=True,string="Delivery Date")

    @api.depends('line_ids.sale_line_ids')
    def get_delivery_date(self):
        for rec in self:
            rec.x_customer_order_delivery_date=''
            if rec.line_ids.sale_line_ids:

                source_orders = rec.line_ids.sale_line_ids.order_id
                sales_ids = self.env['sale.order'].sudo().search([('id', 'in', source_orders.ids)],limit=1,order='x_customer_order_delivery_date desc')
                rec.x_customer_order_delivery_date = sales_ids.x_customer_order_delivery_date





class SaleReport(models.Model):
    _inherit = 'sale.report'

class SaleReport(models.Model):
    _inherit = 'sale.report'
    # pricelist_id = fields.Many2one('product.pricelist','Price List',readonly=True)
    price_unit = fields.Float()

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['x_customer_order_delivery_date'] = "s.x_customer_order_delivery_date"
        # res['pricelist_id'] = "s.pricelist_id"
        res['price_unit'] = "l.price_unit"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
               s.x_customer_order_delivery_date,
               
               l.price_unit
               """
        return res