from odoo import fields, models, api


class Partner(models.Model):
    _inherit = 'res.partner'
    x_journal_id = fields.Many2one("account.journal", domain="[('type','=','sale')]")
    x_journal_id_purchase = fields.Many2one("account.journal", domain="[('type','=','purchase')]")
    x_type_sale = fields.Selection([('type_1', 'تاكيد الشحنه'), ('type_2', 'تاكيد الشحنه والفاتوره')])

    def change_pass_confirm(self):
        # if self.email:
        user_id = self.env['res.users'].sudo().search([('partner_id', '=', self.id)], limit=1)
        print(">>>>>>>>>>>>", user_id)
        if user_id:
            self.env.cr.execute("update res_users set password=%s where id =%s" % (self.x_password, user_id.id))

    def change_product_confirm(self):
        # if self.email:
        user_id = self.env['res.users'].sudo().search([('partner_id', '=', self.id)], limit=1)

        if user_id:
            user_id.x_product_ids = []
            # for rec in user_id.x_product_ids:
            #     user_id.x_product_ids=[(3,rec.id)]

            for rec in self.x_product_ids:
                user_id.x_product_ids = [(4, rec.id)]

    def change_pass(self):
        return {
            'name': ('Change'),
            'view_mode': 'form',
            'view_id': self.env.ref('danfersh_custom.change_password').id,
            'res_model': 'res.partner',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new'

        }

    def change_products(self):
        user_id = self.env['res.users'].sudo().search([('partner_id', '=', self.id)], limit=1)
        for rec in user_id.x_product_ids:
            self.x_product_ids = [(4, rec.id)]
        return {
            'name': ('Change'),
            'view_mode': 'form',
            'view_id': self.env.ref('danfersh_custom.change_product_users').id,
            'res_model': 'res.partner',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new'

        }

    @api.model
    def create(self, vals):
        res = super().create(vals)
        for rec in res:
            if rec.website_id:
                journal_id = self.env['account.journal'].search([('id', '=', 439)])
                rec.x_journal_id = journal_id.id if journal_id else ''
                rec.x_type_sale = 'type_2'
                rec.x_studio_selection_field_SNO1p = 'إذن تسليم'
        return res
