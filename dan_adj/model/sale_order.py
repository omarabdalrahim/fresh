
from odoo import api,fields,models,_

class SaleOrder(models.Model):
    _inherit = "sale.order"

    journal_ids = fields.Many2many('account.journal', compute='_get_journal_tags', string='دفتر اليومية')
    journal_ids_filter = fields.Many2many('account.journal','filter_journal', string='دفتر اليومية')

    @api.depends('invoice_ids')
    def _get_journal_tags(self):
        for rec in self:
            for inv in  rec.invoice_ids:
                for pay in self.env['account.payment'].search([]):
                    print('====', pay.reconciled_invoice_ids)
                    if inv in pay.reconciled_invoice_ids:
                        print('====2', pay.reconciled_invoice_ids)
                        rec.journal_ids += pay.journal_id
            rec.journal_ids_filter = rec.journal_ids
