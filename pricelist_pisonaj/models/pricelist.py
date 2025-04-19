from odoo import api, fields, models, osv
class PriceList(models.Model):
    _inherit = 'product.pricelist.item'
class Product(models.Model):
    _inherit = 'product.product'
    uom_id_new = fields.Many2one('uom.uom',string='Unit of Measure')

    # @api.constrains('uom_id_new')
    # def get_new_uom(self):
    #     stock_move = self.env['stock.move'].search([('product_id', '=', self.id)])
    #     for rec in stock_move:
    #         rec.product_uom = self.uom_id_new.id
    #     stock_move = self.env['sale.order.line'].search([('product_id', '=', self.id)])
    #     for rec in stock_move:
    #         rec.product_uom = self.uom_id_new.id
    #     stock_move = self.env['purchase.order.line'].search([('product_id', '=', self.id)])
    #     for rec in stock_move:
    #         rec.product_uom = self.uom_id_new.id
    #     # stock_move = self.env['mrp.bom'].search([('product_id', '=', self.id)])
    #     # for rec in stock_move:
    #     #     rec.product_uom = self.uom_id_new.id
    #     self.uom_id=self.uom_id_new.id
