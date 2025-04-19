from odoo import models, fields, api


class wizard(models.TransientModel):
    _name = 'sale.order.wizard'
    sale_ids = fields.Many2many(
        comodel_name='sale.order',
        string='')


    def action_credit_note(self):
        lines = []
        partner_ids = []
        body = ''
        body_2 = ''
        for rec in self.sale_ids:

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
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.....P",stock.product_id.name,stock.sale_line_id.order_id.name)
                    lines.append((0, 0, {
                        'product_id': stock.product_id.id,
                        'quantity': stock.quantity_done,
                        'price_unit': stock.sale_line_id.price_unit,
                        'discount':stock.sale_line_id.discount
                    }))
        body3 = ''
        if len(partner_ids) == 1:
            if partner_ids[0].x_journal_id:
                move_id = self.env['account.move'].create({
                    'partner_id': partner_ids[0].id,
                    'move_type': 'out_refund',
                    'invoice_line_ids': lines, 'journal_id': partner_ids[0].x_journal_id.id,
                    'invoice_date': scheduled_date.date() if scheduled_date else ''

                })
            else:
                move_id = self.env['account.move'].create({
                    'partner_id': partner_ids[0].id,
                    'move_type': 'out_refund',

                    'invoice_line_ids': lines,
                    'invoice_date': scheduled_date.date() if scheduled_date else ''

                })
            body3 += (" Create Credit Note <a href=# data-oe-model=account.move data-oe-id=%d>%s</a>") % (
                move_id.id, move_id.name) + ","

            for rec in self.sale_ids:
                rec.x_credit_note_ids = [(4, move_id.id)]
                rec.message_post(body=body3)

            move_id.message_post(body=body)
            move_id.message_post(body=body_2)

        # move_id.action_post()
