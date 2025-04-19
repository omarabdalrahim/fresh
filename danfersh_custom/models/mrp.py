from odoo import fields, models, api


class ModelName(models.Model):
    _inherit = 'mrp.production'
    count_qualtiy = fields.Float(readonly=True)

    # def get_count_qualtiy(self):
    #     for rec in self:
    #         rec.count_qualtiy = 0
    #         if rec.id:
    #             rec.count_qualtiy = len(self.env['quality.alert'].search([('production_id', '=', rec.id)]))

    def create_quality(self):
        self.env['quality.alert'].create({
            'product_id': self.product_id.id,
            'title': self.name,
            'company_id': self.company_id.id,
            'production_id': self.id
        })
        self.count_qualtiy+=1

    def action_view_qualtiy(self):
        action = self.env["ir.actions.act_window"].sudo()._for_xml_id("quality_control.quality_alert_action_check")

        action['domain'] = [('production_id', '=', self.id)]
        action['view_mode'] = 'tree,form'
        return action
