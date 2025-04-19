from odoo import fields, models, api

import itertools
class ModelName(models.Model):
    _inherit = 'stock.picking'
    def action_internal_note(self):
        lcation_id=''
        move_ids_without_package=[]
        lcation_id=''
        for rec in self.move_ids_without_package:
            move_ids_without_package.append({
                'product_id':rec.product_id.id,
                'product_uom_qty':rec.product_uom_qty,
                'name':rec.product_id.name,
                'product_uom':rec.product_uom.id
            })
            lcation_id = rec.picking_id.location_id
        docs = sorted(move_ids_without_package, key=lambda i: (i['product_id'],i['product_uom']))
        lst=[]

        for key, group in itertools.groupby(docs, key=lambda x: (x['product_id'],x['product_uom'])):


            product_id=product_uom=''
            product_uom_qty=0
            for item in group:
                product_uom_qty += item["product_uom_qty"]
                product_uom = item['product_uom']
                product_id=item['product_id']
            lst.append((0, 0, {
                'product_id': product_id,
                'product_uom_qty': product_uom_qty,
                # 'name': rec.product_id.name,
                'product_uom': product_uom_qty
            }))

        view = self.env.ref('stock.view_picking_form')
        picking_id = self.env['stock.picking.type'].search([('default_location_src_id','=',lcation_id.id),\
                                                            ('code','=','internal')],limit=1)
        # move_ids_without_package
        return {
            'name': ('Internal Transfer'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {'default_picking_type_id': picking_id.id, 'default_location_id': lcation_id.id,
           'default_move_ids_without_package':move_ids_without_package},
            'target': 'new'
        }

    def get_last_price(self, sdate, product):
        bom_id = self.env['mrp.bom'].search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)], )
        if bom_id:
            return self.get_last_price_bom(product, 0, sdate)
        purchase_order = self.env['purchase.order.line'].search(
            [('order_id.date_order', '<=', sdate), ('product_id', '=', product.id)], order='id desc', limit=1)
        if purchase_order:
            return purchase_order.price_unit
        else:
            return 0

    def get_last_price_bom(self, product, total, sdate=None):
        bom_id = self.env['mrp.bom'].search(
            [('product_tmpl_id', '=', product.product_tmpl_id.id)])
        print(">>>>>>>>>>>>>>>>>>>..", product.name, total)
        purchase_order = self.env['purchase.order.line'].search(
            [('order_id.date_order', '<=', sdate), ('product_id', '=', product.id)], order='id desc',
            limit=1)
        if purchase_order:
            print(">>>>>>>>>>>>>>>>>>>..", product.name, total)

            total += (purchase_order.price_unit)
        if bom_id:

            for rec in bom_id.bom_line_ids:

                bom_id_2 = self.env['mrp.bom'].search(
                    [('product_tmpl_id', '=', rec.product_id.product_tmpl_id.id)])
                if bom_id_2:
                    total += self.get_last_price_bom(rec.product_id, total) * rec.product_qty
                purchase_order = self.env['purchase.order.line'].search(
                    [('order_id.date_order', '<=', sdate), ('product_id', '=', rec.product_id.id)], order='id desc',
                    limit=1)
                if purchase_order:
                    total += (purchase_order.price_unit * rec.product_qty)

        return total

    def get_last_price_all(self,data):
        res=[]
        for rec in data.move_ids_without_package:
            res.append({
                'product_id':rec.product_id.name,
                'id':rec.product_id.id,
                'qty':rec.product_uom_qty,
                'price':self.get_last_price(rec.picking_id.scheduled_date,rec.product_id)
            })

        docs = sorted(res, key=lambda i: (i['id']))
        print(docs)
        lines=[]
        total_qty=total_price=0

        for key, group in itertools.groupby(docs, key=lambda x: (x['id'])):

            price, quantity, i, j = 0, 0, 0, 0
            lst = {}
            pro=''
            for item in group:
                price += item["price"]
                total_price += item["price"]
                quantity += item["qty"]
                total_qty += item["qty"]
                pro=item["product_id"]
            lines.append({
                'product_id':pro,
                'qty':quantity,
                'price':price,
                'total':quantity*price
            })

        print(">>>>>>>>>.",lines)




        # last_value=[]
        # last_value.append({ 'lines':lines,'total_price':total_price,'total_qty':total_qty})
        return  lines
