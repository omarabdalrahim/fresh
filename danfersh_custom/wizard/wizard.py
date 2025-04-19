import itertools

from odoo import fields, models, api
from odoo import tools

class sales(models.Model):
    _inherit = 'sale.order'
    parent_id = fields.Many2one(related="partner_id.parent_id")

class Wizard(models.Model):
    _name = 'sale.wizard'
    parent_id  = fields.Many2many("res.partner","parent_compau_wizard_parent","parent","id",domain=[('company_type','=','company')])
    partner_id =fields.Many2many("res.partner","parent_compau_wizard","parent","id",domain=[('company_type','!=','company')])
    start_date = fields.Date()
    end_date = fields.Date()

    def print_muli_currency_report(self):
        domin = []
        domin.append(('state','=','sale'))
        domin.append(('company_id','=',self.env.company.id))
        if self.start_date:
            domin.append(('x_customer_order_delivery_date', '>=', self.start_date))
        if self.end_date:
            domin.append(('x_customer_order_delivery_date', '<=', self.end_date))
        if self.partner_id:
            domin.append(('partner_id', 'in', self.partner_id.ids))
        # if self.parent_id:
        #     domin.append(('parent_id', 'in', self.parent_id.ids))
        # if self.journal_ids:
        #     domin.append(('payment_id.journal','in',self.journal_ids))
        lines = self.env['sale.order'].search(domin)
        ids = []
        res = []
        for rec in lines:
            total_inv_dif=total_amount_invoice=total_amount_invoice_return=0
            # if self.parent_id:
            #     if rec.partner_id.parent_id.id in self.parent_id.ids:
            #         for inv in rec.invoice_ids:
            #             if inv.state != 'cancel' and inv.move_type == 'out_invoice':
            #                 total_inv_dif += inv.amount_total
            #             if inv.state != 'cancel' and inv.move_type == 'out_refund':
            #                 total_amount_invoice_return += inv.amount_total
            # else:
            #     for inv in rec.invoice_ids:
            #         if inv.state != 'cancel' and inv.move_type == 'out_invoice':
            #             total_inv_dif += inv.amount_total
            #         if inv.state != 'cancel' and inv.move_type == 'out_refund':
            #             total_amount_invoice_return += inv.amount_total
            for line in rec.order_line:
                res.append({
                    'date': rec.customer_order_delivery_date,
                    'so_name': rec.name,
                    'partner_id': rec.partner_id.id,
                    'parent_id': rec.partner_id.parent_id.id,
                    'parent_name': rec.partner_id.parent_id.name,
                    'partner_name': rec.partner_id.name,
                    'product_name': line.product_id.name,
                    'product_id':line.product_id.id,
                    'product':line.product_id,
                    'delivery':line.qty_delivered,
                    'product_uom_qty':line.product_uom_qty,


                })

        docs_list = []
        if self.parent_id:
            docs_list = []
            docs = sorted(res, key=lambda i: (i['product_id']))
            print(docs)

            for key, group in itertools.groupby(docs, key=lambda x: (x['product_id'])):

                price_total, quantity, i, j = 0, 0, 0, 0
                product = ''
                lst = {}
                delivery = product_uom_qty = return_qty = 0
                date = ''
                so_name = ''
                for item in group:
                    delivery += item['delivery']
                    product_uom_qty += item['product_uom_qty']
                    product = item['product_name']
                    return_qty += item['product_uom_qty'] - item['delivery']
                docs_list.append({
                    'product': product,
                    'product_uom_qty': product_uom_qty,
                    'delivery': delivery,
                    'return': return_qty,
                    'total_1': product_uom_qty - delivery if product_uom_qty - delivery != 0 else delivery,
                    'total_2': ((delivery / product_uom_qty) * 100) if product_uom_qty>0 else 0,
                    'total_3': (return_qty / product_uom_qty) * 100 if product_uom_qty>0 else 0,

                })

        else:
            docs_list = []
            docs = sorted(res, key=lambda i: (i['product_id']))
            print(docs)

            for key, group in itertools.groupby(docs, key=lambda x: (x['product_id'])):

                price_total, quantity, i, j = 0, 0, 0, 0
                product = ''
                lst = {}
                delivery = product_uom_qty =return_qty= 0
                date = ''
                so_name = ''
                for item in group:
                    delivery += item['delivery']
                    product_uom_qty += item['product_uom_qty']
                    product = item['product_name']
                    return_qty+=  item['product_uom_qty']-item['delivery']
                docs_list.append({
                    'product': product,
                    'product_uom_qty': product_uom_qty,
                    'delivery': delivery,
                     'return' :return_qty,
                    'total_1':product_uom_qty-delivery if product_uom_qty-delivery!=0 else delivery,
                    'total_2':((delivery/product_uom_qty)*100),
                    'total_3':(return_qty/product_uom_qty)*100,

                })

        print(docs_list)

        p_ist=[]
        partner_ist=[]
        for rec in self.parent_id:
            p_ist.append({'name':rec.name})
        for rec in self.partner_id:
            name = rec.name
            if rec.parent_id:
                name+="("+rec.parent_id.name+")"
            partner_ist.append({'name':name})
        datas = {
            'ids': self,
            'model': 'sale.wizard',

            'start_date': self.start_date,
            'end_date': self.end_date,
            'lines': docs_list,
            'parent_id':p_ist,
            'partner_ist':partner_ist,

        }
        return self.env.ref('danfersh_custom.action_return_sale_report').report_action([], data=datas)


