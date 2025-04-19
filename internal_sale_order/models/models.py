# -*- coding: utf-8 -*-
import itertools

from odoo import models, fields, api
#
# class order (models.Model):
#     _inherit = 'sale.order'
#     def action_internal_tran(self):
#         return {
#             'name': 'Transfer',
#             'view_mode': 'form',
#             'res_model': 'internal.sales.transfer',
#             'type': 'ir.actions.act_window','target': 'new',
#
#         }

class warehouse(models.TransientModel):
    _name = "internal.sales.transfer"
    warehouse_id = fields.Many2one("stock.warehouse", string="WareHouse")
    dest_warehouse_id = fields.Many2one("stock.warehouse", string="Dest WareHouse")


    sales_order = fields.Many2many('sale.order',
                                  string='Sale Order Line')
    location_id = fields.Many2one(related='warehouse_id.lot_stock_id', string='Location')

    def create_transfer(self):

        picking_type_id = self.env['stock.picking.type'].search([('default_location_dest_id', '=', self.location_id.id),
                                                                 ('code', '=', 'internal')])
        lines = []
        sale_oder_name=''
        for rec in self.sales_order:
            sale_oder_name += rec.name
            for record in rec.order_line:
                    lines.append({ 'product_id': record.product_id.id,
                                         'product_uom_qty': record.product_uom_qty
                        , 'product_uom': record.product_uom.id or ''})
        docs = sorted(lines, key=lambda i: (i['product_id']))

        lst=[]
        picking_id = self.env['stock.picking']

        name, partner_id, journal_enteres_id = '', '', ''
        seq = self.env['ir.sequence'].search([('prefix', '=', 'WH/IN/')])
        seq.number_next_actual += 1
        seq = seq.number_next_actual
        picking_id = self.env['stock.picking']
        picking_id = picking_id.create({
                                        'picking_type_code': 'internal',
                                        'picking_type_id': self.warehouse_id.int_type_id.id,
                                        'location_dest_id': self.dest_warehouse_id.lot_stock_id.id,
                                        'location_id': self.location_id.id, 'origin': sale_oder_name})
        docs = sorted(lines, key=lambda i: (i['product_id']))
        for key, group in itertools.groupby(docs, key=lambda x: (x['product_id'])):
            price_total, quantity, product_uom, product_id = 0, 0, '', ''

            for item in group:

                quantity += item["product_uom_qty"]
                product_id = item['product_id']
                product_uom = item['product_uom']
            lst.append((0, 0, {  'product_id': product_id,
                                 'qty_done': quantity
                , 'product_uom_id':product_uom, 'location_id': self.location_id.id,
                                 'location_dest_id': self.dest_warehouse_id.lot_stock_id.id}))






        picking_id.move_line_ids_without_package = lst
        # picking_id.show_operations = True
        # picking_id.show_reserved = True
        # picking_id.immediate_transfer = True
        # picking_id.sudo().action_confirm()


        view = self.env.ref('stock.view_picking_form')
        return {
            'name': ('Transfer'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'res_id': picking_id.id,
            'context': self.env.context,
            'target':'current',
        }


            #picking_id.action_confirm()
            #pp = picking_id.button_validate()
            # stock_immediate = self.env['stock.immediate.transfer'].search([])
            #
            # for rec in stock_immediate:
            #     for record in rec.pick_ids:
            #         if record.id == picking_id.id:
            #             rec.process()
