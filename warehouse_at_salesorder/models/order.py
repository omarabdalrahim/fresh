import itertools
import logging
from odoo import fields, http, tools, _
from odoo.http import request

_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request
from collections import OrderedDict
from datetime import datetime


class warehouse(models.Model):
    _name = "warehouse.sales"

    warehouse_id = fields.Many2one("stock.warehouse", string="WareHouse")
    sales_order = fields.Many2many("sale.order", "wh", "id", string="Sales order")
    def get_bill_material(self,pro_list,product_ids_qty):
        result,x=[],[]
        qty,index=1,0
        for rec in pro_list:
            bom_id = self.env['mrp.bom'].search(
                [('product_id', '=', rec)], limit=1)
            if bom_id:
                for pro in product_ids_qty:
                    qty_l=0
                    if pro['product_id'].id == rec:
                        stock_qty = self.env['stock.quant'].search([('product_id', '=', rec),
                                                                    ('on_hand', '=', True),
                                                                    ('location_id', '=',
                                                                     self.warehouse_id.lot_stock_id.id)])
                        for l in stock_qty:
                            qty_l+=l.quantity


                        if qty_l<0:
                            qty_l=0
                        qty = pro['qty'] - qty_l



                        if qty<0:
                            qty =1
                        break
                    index+=1
                try:
                    product_ids_qty.pop(index)
                    for bom in bom_id.bom_line_ids:
                        result.append(bom.product_id.id)
                        product_ids_qty.append({'product_id':bom.product_id,'qty':bom.product_qty*qty})
                except IndexError:
                    print("Not found")
            else:
                result.append(rec)

        pro_list.sort()
        result.sort()


        if pro_list == result:
            return False,result,product_ids_qty
        else:

            return True,result,product_ids_qty




    def action_create_po(self):

        product_list, lines = [], []

        for rec in self.sales_order:
            for line in rec.order_line:
                if line.product_id not in product_list:
                    product_list.append(line.product_id)

        for pro in product_list:
            q = 0
            for order in self.sales_order:
                for line in order.order_line:

                    if pro.id == line.product_id.id:
                        q += line.product_uom_qty
            bom_id = self.env['mrp.bom'].search(
                ['|', ('product_id', '=', pro.id), ('product_tmpl_id', '=', pro.product_tmpl_id.id)],
                order='write_date desc', limit=1)
            pro_list,check_pro,product_ids_qty = [],True,[]
            if bom_id:
                stock_qty = self.env['stock.quant'].search([('product_id', '=', pro.id),
                                                            ('on_hand', '=', True),
                                                            ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
                qty_l=0
                for l in stock_qty:
                    qty_l += l.quantity
                if qty_l < 0:
                    qty_l = 0
                bom_qty_available = q - qty_l
                for rec in bom_id.bom_line_ids:
                    pro_list.append(rec.product_id.id)
                    product_ids_qty.append({'product_id': rec.product_id, 'qty': bom_qty_available*rec.product_qty})

                while check_pro==True:
                    check_pro,pro_list,product_ids_qty = self.get_bill_material(pro_list,product_ids_qty)





                for rec in product_ids_qty:
                    qty_l=0

                    stock_qty = self.env['stock.quant'].search([('product_id', '=', rec['product_id'].id),
                                                                ('on_hand', '=', True),
                                                                ('location_id', '=',self.warehouse_id.lot_stock_id.id)])

                    for l in stock_qty:
                        qty_l += l.quantity
                    if qty_l<0:
                        qty_l=0
                    q_requested = rec['qty'] - qty_l


                    if q_requested < 0:
                        q_requested = 0

                    if q_requested > 0:
                        price_unit = 0
                        product_price = ''
                        product_price = self.env['purchase.order.line'].search(
                            [('product_id', '=', rec['product_id'].id), ('price_unit', '>', 0)], order='create_date desc',
                            limit=1)
                        product_price_purchase = self.env['person.purchase.line'].search(
                            [('product_id', '=', rec['product_id'].id), ('purchase_price', '>', 0)],
                            order='create_date desc', limit=1)

                        if product_price_purchase and product_price:
                            if product_price_purchase.create_date > product_price.create_date and product_price_purchase.purchase_price > 0:
                                price_unit = product_price_purchase.purchase_price
                        elif product_price.price_unit > 0 and price_unit == 0:
                            price_unit = product_price.price_unit
                        elif product_price_purchase.purchase_price > 0 and price_unit == 0:
                            price_unit = product_price_purchase.purchase_price


                        lines.append({'product_id': rec['product_id'].id, "product_qty": q_requested,
                                      "product_uom": rec['product_id'].uom_id.id,
                                      'name': rec['product_id'].name, 'date_planned': datetime.now(), 'taxes_id': [(5,)],
                                      'price_unit': price_unit})


            else:
                stock_qty = self.env['stock.quant'].search([('product_id', '=', pro.id),
                                                            ('on_hand', '=', True),
                                                            ('location_id', '=', self.warehouse_id.lot_stock_id.id)])

                qty_l=0
                for l in stock_qty:
                    qty_l += l.quantity
                if qty_l < 0:
                    qty_l = 0
                q_requested = q - qty_l

                if q_requested < 0:
                    q_requested = 0

                if q_requested > 0:
                    price_unit = 0
                    product_price = ''
                    product_price = self.env['purchase.order.line'].search(
                        [('product_id', '=', pro.id), ('price_unit', '>', 0)], order='create_date desc',
                        limit=1)
                    product_price_purchase = self.env['person.purchase.line'].search(
                        [('product_id', '=', pro.id), ('purchase_price', '>', 0)],
                        order='create_date desc', limit=1)
                    if product_price_purchase and product_price:
                        if product_price_purchase.create_date > product_price.create_date and product_price_purchase.purchase_price > 0:
                            price_unit = product_price_purchase.purchase_price
                    elif product_price.price_unit > 0:
                        price_unit = product_price.price_unit
                    elif product_price_purchase:
                        price_unit = product_price_purchase.purchase_price

                    lines.append({'product_id': pro.id, "product_qty": q_requested, 'pro_name': pro.name,
                                  "product_uom": pro.uom_id.id, 'name': pro.name,
                                  'date_planned': datetime.now(), 'taxes_id': [(5,)], 'price_unit': price_unit})

        purchase_order = self.env['purchase.order']
        picking_type = self.env['stock.picking.type'].search(
            [('code', '=', 'incoming'), ('defualt_warhouse_purchase', '=', True)])
        picking_type_id = 0
        vendor = self.env['res.partner'].search([('default_purchase_oer', '=', True)]).id
        for rec in picking_type:
            picking_type_id = rec.id
            break
        lst = []
        docs = sorted(lines, key=lambda i: (i['product_id']))
        for key, group in itertools.groupby(docs, key=lambda x: (x['product_id'])):
            price_total, quantity, product_uom, product_id, price_unit, pro_name = 0, 0, '', '', 0, ''

            for item in group:

                quantity += item["product_qty"]
                product_id = item['product_id']
                product_uom = item['product_uom']
                if item['price_unit'] > 0:
                    price_unit = item['price_unit']
                pro_name = item['name']
            lst.append({'product_id': product_id, "product_qty": quantity,
                        "product_uom": product_uom, 'name': pro_name,
                        'date_planned': datetime.now(), 'taxes_id': [(5,)], 'price_unit': price_unit})

        return {'name': 'Purchase order',
                'res_model': 'purchase.order',
                'target': 'new',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('purchase.purchase_order_form').id,

                'context': {'default_order_line': lst, 'default_picking_type_id': picking_type_id,
                            'default_partner_id': vendor},
                'type': 'ir.actions.act_window', }


class stock_warhouse(models.Model):
    _inherit = 'stock.warehouse'
    defualt_warhouse = fields.Boolean("default warehouse ", default=False)


class Picking(models.Model):
    _inherit = 'stock.picking.type'
    defualt_warhouse_purchase = fields.Boolean("default warehouse Purchase", default=False)