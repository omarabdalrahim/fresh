# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round

class change_product(models.TransientModel):
    _name = 'product.change'
    product_id = fields.Many2one("product.product", )
    product_uom = fields.Many2one("uom.uom", )
    qty = fields.Float()
    pick_id = fields.Many2one("stock.return.picking")

    @api.onchange('product_id')
    def _onchnage_product_uom(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id


class ReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'
    is_sales_order = fields.Boolean()
    change = fields.Boolean()
    change_product_ids = fields.One2many("product.change", "pick_id")
    scheduled_date = fields.Datetime(default=lambda self: fields.Datetime.now())

    @api.onchange('picking_id')
    def _onchange_picking_id(self):
        move_dest_exists = False
        product_return_moves = [(5,)]
        if self.picking_id and self.picking_id.state != 'done':
            raise UserError(_("You may only return Done pickings."))
        # In case we want to set specific default values (e.g. 'to_refund'), we must fetch the
        # default values for creation.
        line_fields = [f for f in self.env['stock.return.picking.line']._fields.keys()]
        product_return_moves_data_tmpl = self.env['stock.return.picking.line'].default_get(line_fields)
        for move in self.picking_id.move_ids:
            if move.state == 'cancel':
                continue
            if move.scrapped:
                continue
            if move.move_dest_ids:
                move_dest_exists = True
            product_return_moves_data = dict(product_return_moves_data_tmpl)
            product_return_moves_data.update(self._prepare_stock_return_picking_line_vals_from_move(move))
            product_return_moves.append((0, 0, product_return_moves_data))
        if self.picking_id and not product_return_moves:
            raise UserError(
                _("No products to return (only lines in Done state and not fully returned yet can be returned)."))
        if self.picking_id and not self.original_location_id:
            self.product_return_moves = product_return_moves
            self.move_dest_exists = move_dest_exists
            self.parent_location_id = self.picking_id.picking_type_id.warehouse_id and self.picking_id.picking_type_id.warehouse_id.view_location_id.id or self.picking_id.location_id.location_id.id
            self.original_location_id = self.picking_id.location_id.id
            location_id = self.picking_id.location_id.id
            if self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.return_location:
                location_id = self.picking_id.picking_type_id.return_picking_type_id.default_location_dest_id.id
            self.location_id = location_id

    def _create_returns(self):
        new_picking_2, picking_type_id = super(ReturnPicking, self)._create_returns()
        if self.is_sales_order:

            new_picking = self.env['stock.picking'].search([('id', '=', new_picking_2)])
            new_picking.scheduled_date = self.scheduled_date
            picking_type_id = self.env['stock.warehouse'].search(
                [('id', '=', self.location_id.warehouse_id.id)], limit=1).in_type_id
            body_2 = ''
            if new_picking and new_picking.sale_id:


                if new_picking.scheduled_date:
                    sale_id = self.env['sale.order'].search(
                        [('x_customer_order_delivery_date', '>=',
                          (new_picking.scheduled_date + datetime.timedelta(hours=2)).date()),
                         ('partner_id', '=', new_picking.sale_id.partner_id.id),
                         ('state', 'in', ('sale', 'done'))] \
                        , order='x_customer_order_delivery_date asc', limit=1)
                    print(">>>>>>>>>>>>88888.", sale_id, new_picking.scheduled_date)
                else:
                    sale_id = self.env['sale.order'].search(
                        [('x_customer_order_delivery_date', '>', new_picking.sale_id.x_customer_order_delivery_date),
                         ('partner_id', '=', new_picking.sale_id.partner_id.id),
                         ('state', 'in', ('sale', 'done'))] \
                        , order='id desc', limit=1)
                body_2 += (" <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                    sale_id.id, sale_id.name) + ","
                new_picking.message_post(body=body_2)
                # new_picking.action_assign()
                immediate_transfer = self.env['stock.immediate.transfer'].sudo().create({

                })
                self.env['stock.immediate.transfer.line'].sudo().create({
                    'immediate_transfer_id': immediate_transfer.id,
                    'picking_id': new_picking.id,
                    'to_immediate': True
                })
                picking_type_id = self.env['stock.picking.type'].sudo().search(
                    [('code', '=', 'outgoing'), ('default_location_dest_id', '=', self.location_id.id)], limit=1)

                immediate_transfer.sudo().process()
                # new_picking.sudo().write({
                #     'picking_type_id':picking_type_id.id
                # })

                new_picking.button_validate()

                if self.change:
                    move_ids_without_package = []
                    change_id = ''
                    for l in self.product_return_moves:
                        move_ids_without_package.append((0, 0, {
                            'product_id': l.product_id.id,
                            'name': l.product_id.name,
                            'product_uom_qty': l.quantity,
                            'quantity_done': l.quantity,
                            'product_uom': l.uom_id.id,
                            'location_dest_id': self.picking_id.location_dest_id.id,
                            'location_id': self.location_id.id,

                        }))
                    picking_type_id = self.env['stock.picking.type'].sudo().search([('code','=','outgoing'),('default_location_src_id','=',self.location_id.id)],limit=1)
                    change_id = self.env['stock.picking'].sudo().create({
                        'picking_type_id': picking_type_id.id,
                        'partner_id': self.picking_id.partner_id.id if self.picking_id.partner_id else '',
                        'location_dest_id': self.picking_id.location_dest_id.id,
                        'location_id': self.location_id.id,
                        'move_ids_without_package': move_ids_without_package,
                        'scheduled_date': self.scheduled_date
                    })

                    try:
                        change_id.action_confirm()
                        change_id.action_assign()
                        if change_id.state=='assigned':
                            immediate_transfer = self.env['stock.immediate.transfer'].sudo().create({

                            })

                            self.env['stock.immediate.transfer.line'].sudo().create({
                                'immediate_transfer_id': immediate_transfer.id,
                                'picking_id': change_id.id,
                                'to_immediate': True
                            })
                            immediate_transfer.sudo().process()
                            change_id.button_validate()
                    except:
                        print('')
                    change_id.scheduled_date = self.scheduled_date


                if sale_id:
                    sale_id.x_last_picking_id_1 = [(4, new_picking_2)]



             
        return new_picking_2, picking_type_id


class Sale(models.Model):
    _inherit = 'sale.order'
    return_date = fields.Datetime()
    return_location_id = fields.Many2one("stock.location")

    return_count = fields.Integer(compute='get_return_count', store=True)
    x_last_picking_id_1 = fields.Many2many(
        comodel_name='stock.picking',
        string='LAst Transfer')
    change = fields.Boolean()

    # @api.model
    # def write(self,vals):
    #     res = super(Sale, self).write(vals)
    #     if self.company_id.id==1 and self.state=='sent':
    #         # self.state='draft'
    #         attachment_id = self.env['ir.attachment'].sudo().search([('res_model','=','sale.order'),\
    #                                                           ("res_id","=",self.id)])
    #         print(">>>>>>>>>>>>>>>>>>>>>.",attachment_id,self.id)
    #         if attachment_id:
    #             attachment_id.sudo().unlink()
    #
    #     return res

    @api.depends('state', 'x_last_picking_id_1')
    def get_return_count(self):
        for rec in self:
            rec.return_count = 0
            # picking_id = self.env['stock.picking'].search([('sale_id', '=', rec.id), \
            #                                                ('picking_type_id.code', '=', 'incoming')])

            # rec.return_count = len(picking_id)
            rec.return_count += len(rec.x_last_picking_id_1)

    def view_retun_picking(self):
        ids = []
        picking_ids = self.env['stock.picking'].search([('sale_id', '=', self.id)])
        # for l in picking_ids:
        #     ids.append(l.id)
        for rec in self.x_last_picking_id_1:
            ids.append(rec.id)

        return {
            'name': ('Return'),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', ids), ('picking_type_id.code', '=', 'incoming')],

            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def view_return_last(self):
        sale_id = self.env['sale.order'].search(
            [('x_customer_order_delivery_date', '<=', self.x_customer_order_delivery_date),
             ('partner_id', '=', self.partner_id.id), ('state', 'in', ('sale', 'done'))] \
            , order='x_customer_order_delivery_date desc', limit=6)
        for rec in sale_id:
            rec.return_date = self.x_customer_order_delivery_date
            rec.return_location_id = self.warehouse_id.lot_stock_id.id
            rec.change=False
        return {
            'name': ('Return'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sales.order.return',
            'context': {'default_partner_id': self.partner_id.id,
                        'default_scheduled_date': self.return_date if self.return_date else datetime.datetime.now(),
                        'default_sales_ids': [(4, rec.id) for rec in sale_id],
                        'default_change':False,
                        },
            'type': 'ir.actions.act_window',
            'target': 'new'
        }
    def view_return_last_change(self):
        sale_id = self.env['sale.order'].search(
            [('x_customer_order_delivery_date', '<=', self.x_customer_order_delivery_date),
             ('partner_id', '=', self.partner_id.id), ('state', 'in', ('sale', 'done'))] \
            , order='x_customer_order_delivery_date desc', limit=6)
        for rec in sale_id:
            rec.return_date = self.x_customer_order_delivery_date
            rec.return_location_id = self.warehouse_id.lot_stock_id.id
            rec.change = True

        return {
            'name': ('تبديل'),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'sales.order.return',
            'context': {'default_partner_id': self.partner_id.id,
                        'default_scheduled_date': self.return_date if self.return_date else datetime.datetime.now(),
                        'default_sales_ids': [(4, rec.id) for rec in sale_id],

                        },
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def return_delivery_sale_order(self):
        picking_id = self.env['stock.picking'].search([('sale_id', '=', self.id) \
                                                          , ('picking_type_id.code', '=', 'outgoing'),
                                                       ('state', '=', 'done')],limit=1,order='id asc')

        if not picking_id:
            return False
        sale_id = self.env['sale.order'].search(
            [('x_customer_order_delivery_date', '>', self.x_customer_order_delivery_date),
             ('partner_id', '=', self.partner_id.id), ('state', 'in', ('sale', 'done'))] \
            , order='x_customer_order_delivery_date asc', limit=1)
        if len(picking_id) > 1:
            return {
                'name': ('Delivery'),
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'domain': [('sale_id', '=', self.id), ('picking_type_id.code', '=', 'outgoing')],

                'type': 'ir.actions.act_window',
                'target': 'current'
            }
        else:
            return {
                'name': ('Return'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'stock.return.picking',
                'context': {'default_picking_id': picking_id.id,
                            'default_is_sales_order': True,
                            'default_change': self.change,
                            'default_scheduled_date': self.return_date if self.return_date else datetime.datetime.now(),
                            # 'default_original_location_id': self.return_location_id.id if self.return_location_id else '',
                            # 'default_location_id': self.return_location_id.id if self.return_location_id else '',
                            },
                'type': 'ir.actions.act_window',
                'target': 'new'
            }

    def return_delivery_sale_order_change(self):
        picking_id = self.env['stock.picking'].search([('sale_id', '=', self.id) \
                                                          , ('picking_type_id.code', '=', 'outgoing'),
                                                       ('state', '=', 'done')])

        if not picking_id:
            return False
        sale_id = self.env['sale.order'].search(
            [('x_customer_order_delivery_date', '>', self.x_customer_order_delivery_date),
             ('partner_id', '=', self.partner_id.id), ('state', 'in', ('sale', 'done'))] \
            , order='x_customer_order_delivery_date asc', limit=1)
        if len(picking_id) > 1:
            return {
                'name': ('Delivery'),
                'view_mode': 'tree,form',
                'res_model': 'stock.picking',
                'domain': [('sale_id', '=', self.id), ('picking_type_id.code', '=', 'outgoing')],

                'type': 'ir.actions.act_window',
                'target': 'current'
            }
        else:
            return {
                'name': ('Return'),
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'stock.return.picking',
                'context': {'default_picking_id': picking_id.id, 'default_is_sales_order': True, 'default_change': True,
                            'default_scheduled_date': self.x_customer_order_delivery_date if self.x_customer_order_delivery_date else datetime.datetime.now(),
                            # 'default_original_location_id': self.return_location_id.id if self.return_location_id else '',
                            # 'default_location_id': self.return_location_id.id if self.return_location_id else '',
                            },
                'type': 'ir.actions.act_window',
                'target': 'new'
            }


class return_from_sales_order(models.TransientModel):
    _name = 'sales.order.return'
    partner_id = fields.Many2one("res.partner", string="Customer")
    sales_ids = fields.Many2many('sale.order', "ii", "id",
                                 string='Sales_ids')
    scheduled_date = fields.Datetime(default=lambda self: fields.Datetime.now())
    change = fields.Boolean()

class Picking(models.Model):
    _inherit = 'stock.picking'
    def _set_scheduled_date(self):
        for picking in self:
            # if picking.state in ('done', 'cancel'):
            #
            #     raise UserError(_("You cannot change the Scheduled Date on a done or cancelled transfer."))
            picking.move_ids.write({'date': picking.scheduled_date})

