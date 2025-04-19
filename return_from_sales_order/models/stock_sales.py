from odoo import fields, models, api
# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_round



class Sale(models.Model):
    _inherit = "sale.order"
    return_date = fields.Datetime()
    return_location_id = fields.Many2one("stock.location")

    return_count = fields.Integer(compute='get_return_count', store=True)
    x_last_picking_id_1 = fields.Many2many(
        comodel_name='stock.picking',
        string='LAst Transfer')
    is_change = fields.Boolean()



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
            rec.is_change = False



        return {
            "name": _("Return"),
            "view_mode": "form",
            "res_model": "sales.order.return",
            "context": {"default_partner_id": self.partner_id.id,
                        "default_scheduled_date": self.return_date if self.return_date else datetime.datetime.now(),
                        "default_sales_ids": [(4, rec.id) for rec in sale_id],
                        "default_change": False,
                        },
            "type": "ir.actions.act_window",
            "target": "new"
        }

    def view_return_last_change(self):
        sale_id = self.env['sale.order'].search(
            [('x_customer_order_delivery_date', '<=', self.x_customer_order_delivery_date),
             ('partner_id', '=', self.partner_id.id), ('state', 'in', ('sale', 'done'))] \
            , order='x_customer_order_delivery_date desc', limit=6)
        for rec in sale_id:
            rec.return_date = self.x_customer_order_delivery_date
            rec.return_location_id = self.warehouse_id.lot_stock_id.id
            rec.is_change = True

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
                                                       ('state', '=', 'done')], limit=1, order='id asc')

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

class Picking(models.Model):
    _inherit = "stock.picking"

    def _set_scheduled_date(self):
        for picking in self:
            # if picking.state in ('done', 'cancel'):
            #
            #     raise UserError(_("You cannot change the Scheduled Date on a done or cancelled transfer."))
            picking.move_ids.write({'date': picking.scheduled_date})