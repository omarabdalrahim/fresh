import itertools

from odoo.exceptions import ValidationError

from odoo import fields, models, api

PAYMENT_STATE_SELECTION = [
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_amount_invoice = fields.Float(compute='get_total_amount_invoice', store=True)

    total_payment = fields.Float(compute='get_total_amount_invoice', store=True)
    total_amount_invoice_return = fields.Float(compute='get_total_amount_invoice', store=True,
                                               string="اجمالي المرتجع فواتير")

    total_payment_return = fields.Float(compute='get_total_amount_invoice', store=True, string="اجمالي المرتجع فلوس")
    total_inv_dif = fields.Float(compute='get_total_amount_invoice', store=True, string="صافي الفواتير")
    total_payment_dif = fields.Float(compute='get_total_amount_invoice', store=True, string="صافي المدوعات")
    totall_payment_prec = fields.Float(compute='get_total_amount_invoice', store=True, string="  نسبه الدفع")
    totall_inv_prec = fields.Float(compute='get_total_amount_invoice', store=True, string="  نسبه التوصيل")
    totall_payment_remaining = fields.Float(compute='get_total_amount_invoice', store=True, string="متبقي الدفع")
    totall_inv_delivery_remaining = fields.Float(compute='get_total_amount_invoice', store=True, string="متبقي التسليم")
    totall_actual_remaining = fields.Float(compute='get_total_amount_invoice', store=True, string="متبقي التحصيل")
    transfer_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], compute='get_transfer_invoice_payment_state', string="Transfer State", index=True)
    transfer_state_filter = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string="Transfer State", index=True)
    invoice_state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled'),
    ], compute='get_transfer_invoice_payment_state', string="invoice State", store=True, index=True)
    payment_state = fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status",
                                     compute='get_transfer_invoice_payment_state', index=True)
    payment_state_filter = fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status", index=True)
    x_journal_id = fields.Many2one(related='partner_id.x_journal_id', store=True, index=True)
    purchaseorderreference = fields.Char()

    # transfer_state_3 = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('waiting', 'Waiting Another Operation'),
    #     ('confirmed', 'Waiting'),
    #     ('assigned', 'Ready'),
    #     ('done', 'Done'),
    #     ('cancel', 'Cancelled'),
    # ],  string="Transfer State",  )
    # invoice_state_3 = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('posted', 'Posted'),
    #     ('cancel', 'Cancelled'),
    # ],  string="invoice State", )
    # payment_state_3 = fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status",
    #                                  )

    @api.model
    def _default_warehouse_id(self):
        # !!! Any change to the default value may have to be repercuted
        # on _init_column() below.
        return self.env.user._get_default_warehouse_id()

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id, check_company=True, track_visibility='onchange')

    def action_reset_invoice(self):
        for rec in self.search([('id', 'in', self.ids)]):
            if rec.invoice_status == 'invoiced':
                rec.invoice_status = 'to invoice'
                for line in rec.order_line:
                    line.qty_invoiced = 0

    @api.onchange('partner_id')
    def _onchange_template_order(self):
        if self.partner_id.x_template_id:
            self.sale_order_template_id = self.partner_id.x_template_id.id

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.partner_id.x_tax_id:
            print(">>>>>>>>>>>>>>>>>>>>>.", res.partner_id.x_tax_id.name)
            for rec in res.order_line:
                if rec.tax_id:
                    if res.partner_id.x_tax_id.id not in rec.tax_id.ids:
                        rec.tax_id = [(4, res.partner_id.x_tax_id.id)]
                else:
                    rec.tax_id = [(4, res.partner_id.x_tax_id.id)]
        if res.partner_id.x_discount:
            for rec in res.order_line:
                rec.discount = res.partner_id.x_discount

        return res

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if 'state' in vals:
            if vals['state'] == 'sent':
                if self.partner_id.x_tax_id:
                    for rec in self.order_line:
                        if rec.tax_id:
                            if self.partner_id.x_tax_id.id not in rec.tax_id.ids:
                                rec.tax_id = [(4, self.partner_id.x_tax_id.id)]
                        else:
                            rec.tax_id = [(4, self.partner_id.x_tax_id.id)]
                if self.partner_id.x_discount:
                    for rec in self.order_line:
                        rec.discount = self.partner_id.x_discount
                if self.company_id.id == 1 and self.website_id:
                    self.partner_invoice_id = self.partner_id.commercial_partner_id.id if self.partner_id.commercial_partner_id else ''

        return res

    @api.depends('invoice_ids', 'state', 'invoice_count', 'write_date', 'order_line.invoice_lines')
    def get_transfer_invoice_payment_state(self):
        for rec in self:
            rec.transfer_state = rec.invoice_state = 'draft'
            rec.transfer_state_filter = rec.invoice_state = 'draft'
            rec.payment_state = 'not_paid'
            rec.payment_state_filter = 'not_paid'
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
            # if rec.id:
            # picking_ids = self.env['stock.picking'].search(
            #     [('sale_id', '=', rec.id), ('picking_type_code', '=', 'outgoing')],limit=1,)
            # if picking_ids:
            #     rec.transfer_state=picking_ids.state

            for pick in rec.picking_ids:
                if pick.picking_type_code == 'outgoing':
                    rec.transfer_state = pick.state
                    rec.transfer_state_filter = pick.state

            for inv in rec.invoice_ids:
                if inv.move_type == 'out_invoice':
                    rec.invoice_state = inv.state
                    rec.payment_state = inv.payment_state
                    rec.payment_state_filter = inv.payment_state
            # rec.invoice_state_3=rec.invoice_state
            # rec.payment_state_3=rec.payment_state
            # rec.transfer_state_3=rec.transfer_state

    def get_transfer_invoice_payment_state_2(self):
        for rec in self.env['sale.order'].search([]):
            rec.transfer_state = rec.invoice_state = 'draft'
            rec.transfer_state_filter = rec.invoice_state = 'draft'
            rec.payment_state = 'not_paid'
            rec.payment_state_filter = 'not_paid'
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.")
            # if rec.id:
            # picking_ids = self.env['stock.picking'].search(
            #     [('sale_id', '=', rec.id), ('picking_type_code', '=', 'outgoing')],limit=1,)
            # if picking_ids:
            #     rec.transfer_state=picking_ids.state

            for pick in rec.picking_ids:
                if pick.picking_type_code == 'outgoing':
                    rec.transfer_state = pick.state
                    rec.transfer_state_filter = pick.state

            for inv in rec.invoice_ids:
                if inv.move_type == 'out_invoice':
                    rec.invoice_state = inv.state
                    rec.payment_state = inv.payment_state
                    rec.payment_state_filter = inv.payment_state
            # rec.invoice_state_3=rec.invoice_state
            # rec.payment_state_3=rec.payment_state
            # rec.transfer_state_3=rec.transfer_state

    def get_qty_all_order_print(self, docs):
        products = []
        for rec in docs:
            for so in rec.order_line:
                products.append({
                    'id': so.product_id.id,
                    'product_id': so.product_id.name,
                    'qty': so.product_uom_qty
                })
        docs = sorted(products, key=lambda i: (i['id']))

        lst = []
        for key, group in itertools.groupby(docs, key=lambda x: (x['id'])):

            pro, quantity, i, j = 0, 0, 0, 0
            # lst = {}

            for item in group:
                quantity += item["qty"]
                pro = item["product_id"]

            lst.append({
                'product_id': pro,
                'qty': quantity

            })
        return lst

    @api.depends('invoice_ids', 'invoice_count', 'totall_payment_prec', 'order_line.invoice_lines')
    def get_total_amount_invoice(self):
        for rec in self:
            rec.total_amount_invoice = rec.total_payment = 0
            rec.total_amount_invoice_return = rec.total_payment_return = 0
            rec.total_inv_dif = rec.total_payment_dif = rec.totall_payment_prec = 0
            rec.totall_inv_prec = rec.totall_payment_remaining = rec.totall_inv_delivery_remaining = 0
            rec.totall_actual_remaining = 0
            for inv in rec.invoice_ids:
                if inv.state != 'cancel' and inv.move_type == 'out_invoice':
                    if self.get_invoice_down_payment(inv) == False:
                        rec.total_amount_invoice += inv.amount_total
                        rec.total_payment += (inv.amount_total - inv.amount_residual)
                if inv.state != 'cancel' and inv.move_type == 'out_refund':
                    rec.total_amount_invoice_return += inv.amount_total
                    rec.total_payment_return += (inv.amount_total - inv.amount_residual)
            rec.total_inv_dif = rec.total_amount_invoice - rec.total_amount_invoice_return
            rec.total_payment_dif = rec.total_payment - rec.total_payment_return
            rec.totall_payment_prec = (rec.total_payment / rec.amount_total) * 100 if rec.amount_total > 0 else 0
            rec.totall_inv_prec = (rec.total_amount_invoice / rec.amount_total) * 100 if rec.amount_total > 0 else 0
            rec.totall_payment_remaining = rec.amount_total - rec.total_payment_dif
            rec.totall_inv_delivery_remaining = rec.amount_total - rec.total_inv_dif
            rec.totall_actual_remaining = rec.total_inv_dif - rec.total_payment_dif

    def get_invoice_down_payment(self, inv):
        for rec in inv.invoice_line_ids:
            if rec.product_id.x_down_payment:
                return True
        return False


    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     res = super(SaleOrder, self)._create_invoices()
    #
    #     for rec in res:
    #         if rec.partner_id.x_journal_id:
    #             rec.journal_id = rec.partner_id.x_journal_id.id
    #             # if self.purchaseorderreference:
    #             #     rec.ref = self.purchaseorderreference
    #             # res.purchaseorderreference = rec.purchaseorderreference
    #     # for rec in res:
    #     #     res['ref'] = rec.purchaseorderreference
    #     return res

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.purchaseorderreference:
            res['ref'] = self.purchaseorderreference
        if self.partner_id.x_journal_id:
            res['journal_id']=self.partner_id.x_journal_id.id
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        check_1 = False
        if self.partner_id.x_purchaseorderreference:
            if not self.purchaseorderreference:
                raise ValidationError("من فضلك ادخل الرقم المرجعي للاذن")
        if self.partner_id.x_type_sale:
            if self.partner_id.x_type_sale in ('type_1', 'type_2'):
                picking_ids = self.env['stock.picking'].search(
                    [('sale_id', '=', self.id), ('picking_type_code', '=', 'outgoing'),
                     ('state', 'not in', ('cancel', 'done'))])
                print("=============", picking_ids)
                for rec in picking_ids:
                    rec.action_assign()
                    if rec.show_check_availability == False:
                        wizard_id = self.env['stock.immediate.transfer'].create({})
                        wizard_id.pick_ids = [(4, rec.id)]
                        wizard_id_line = self.env['stock.immediate.transfer.line'].create({
                            'picking_id': rec.id,
                            'immediate_transfer_id': wizard_id.id,
                            'to_immediate': True
                        })
                        wizard_id.process()

                        rec.button_validate()
                    if rec.state == 'done':
                        check_1 = True
            if self.partner_id.x_type_sale == 'type_2' and check_1:
                move_id = self._create_invoices()
                move_id.action_post()
        return res
