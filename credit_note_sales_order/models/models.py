# -*- coding: utf-8 -*-

from odoo import models, fields, api


class credit_note_sales_order(models.Model):
    _inherit = 'sale.order'
    x_count_credit_note = fields.Integer(compute='get_x_count_credit_note')
    x_total_credit_note = fields.Float(compute='get_x_count_credit_note', string="اجمالي المرتجع")
    x_credit_note_ids = fields.Many2many(
        comodel_name='account.move',
        string='')

    @api.depends('x_credit_note_ids')
    def get_x_count_credit_note(self):
        for rec in self:
            rec.x_count_credit_note = 0
            rec.x_total_credit_note = 0
            if rec.x_credit_note_ids:
                rec.x_count_credit_note = len(rec.x_credit_note_ids)
                # print(">>>>>>>>>>>>>>",(rec.x_credit_note_ids.filtered(lambda x: x.state != 'cancel')))
                rec.x_total_credit_note = sum(
                    x.amount_total if x.state != 'cancel' else 0 for x in rec.x_credit_note_ids)

    def preview_credit_note(self):
        view = self.env.ref('account.view_out_credit_note_tree')
        view_form = self.env.ref('account.view_move_form')
        return {
            'name': ('Credit Note'),
            'view_mode': 'tree,form',
            'view_type': 'form',
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            'res_model': 'account.move',
            'domain': [('id', 'in', self.x_credit_note_ids.ids)],
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_credit_note_view(self):

        return {
            'name': ('Credit Note'),
            'view_mode': 'form',
            'view_id': self.env.ref('credit_note_sales_order.sale_credit_view_form_2').id,
            'res_model': 'sale.order.wizard',
            'context':{'default_sale_ids':[(4,rec.id)for rec in self]},
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

    def action_credit_note(self):
        lines = []
        partner_ids = []
        body = ''
        body_2 = ''
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..")
        for rec in self:
            print("******************************", rec)

            if rec.x_last_picking_id_1:
                if rec.partner_id not in partner_ids:
                    partner_ids.append(rec.partner_id)
                picking_id = self.env['stock.picking'].search(
                    [('id', 'in', rec.x_last_picking_id_1.ids), ('state', '=', 'done')], order='scheduled_date asc')

                scheduled_date = ''
                for r in picking_id:
                    scheduled_date = r.scheduled_date
                    body += (" <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>") % (
                        r.id, r.name) + ","
                    if r.sale_id:
                        body_2 += (" <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                            r.sale_id.id, r.sale_id.name) + ","
                for stock in picking_id.move_ids_without_package:
                    lines.append((0, 0, {
                        'product_id': stock.product_id.id,
                        'quantity': stock.quantity_done,
                        'price_unit': stock.sale_line_id.price_unit
                    }))
        body3 = ''
        if len(partner_ids) == 1:

            move_id = self.env['account.move'].create({
                'partner_id': partner_ids[0].id,
                'move_type': 'out_refund',
                'invoice_line_ids': lines,
                'invoice_date': scheduled_date.date() if scheduled_date else ''

            })
            body3 += (" Create Credit Note <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                move_id.id, move_id.name) + ","

            for rec in self:
                rec.x_credit_note_ids = [(4, move_id.id)]

            move_id.message_post(body=body)
            move_id.message_post(body=body_2)
            self.message_post(body=body3)
            # move_id.action_post()
