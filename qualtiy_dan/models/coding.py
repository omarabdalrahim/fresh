from odoo import fields, models, api


class actioncodeing(models.Model):
    _name = 'action.coding'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Action Coding'
    active = fields.Boolean(default=True)

    name = fields.Char(required=1)
    name_arabic = fields.Char(required=1,string="الاسم العربي")
    code = fields.Char()
    display_name2 = fields.Char(compute='_compute_display_name2')
    bands_ids = fields.Many2many("band.action","band_action_code_action","action_id","id")
    first_page_ids = fields.Many2one("page.action.first", store=True, compute='get_first_page_id' ,string="البنود المرتبطه")
    @api.model
    def get_first_page_id(self):
        for rec in self:
            rec.first_page_ids = []
            if rec.id:
                first_page_id = self.env['page.action.first'].search([('action_id', '=', rec.id)])
                for page in first_page_id:
                    rec.first_page_ids = page.id



    @api.depends('code', 'name')
    def _compute_display_name2(self):
        for rec in self:
            rec.display_name2 = ''
            if rec.name and rec.code:
                rec.display_name2 = rec.name + "/" + rec.code

    @api.model
    def create(self, vals):
        res = super(actioncodeing, self).create(vals)
        res.code = self.env["ir.sequence"].next_by_code("actioncoding")
        return res


class modelcodeing(models.Model):
    _name = 'model.coding'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Action Coding'
    _rec_name = 'display_name'
    active = fields.Boolean(default=True)

    name = fields.Char(required=1)
    seq = fields.Char()
    code = fields.Char(compute='_get_code')
    display_name2 = fields.Char(compute='_compute_display_name2')
    coding_id = fields.Many2one('action.coding', required=True)

    @api.depends('code', 'seq')
    def _compute_display_name2(self):
        for rec in self:
            rec.display_name2 = ''
            if rec.name and rec.code:
                rec.display_name2 = rec.code + "." + rec.name

    @api.depends('coding_id')
    def _get_code(self):
        for rec in self:
            rec.code = ''
            if rec.coding_id and rec.seq:
                rec.code =  rec.coding_id.code+"."+rec.seq


    @api.model
    def create(self, vals):
        res = super(modelcodeing, self).create(vals)
        res.seq = self.env["ir.sequence"].next_by_code("actionmodel")
        return res
class model_instruction(models.Model):
    _name = 'model.instruction'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Action instruction'
    _rec_name = 'display_name'
    active = fields.Boolean(default=True)

    name = fields.Char(required=1)
    seq = fields.Char()
    code = fields.Char(compute='_get_code')
    display_name2 = fields.Char(compute='_compute_display_name2')
    coding_id = fields.Many2one('action.coding', required=True)

    @api.depends('code', 'seq')
    def _compute_display_name2(self):
        for rec in self:
            rec.display_name2 = ''
            if rec.name and rec.code:
                rec.display_name2 = rec.code + "." + rec.name

    @api.depends('coding_id')
    def _get_code(self):
        for rec in self:
            rec.code = ''
            if rec.coding_id and rec.seq:
                rec.code =  rec.coding_id.code+"."+rec.seq


    @api.model
    def create(self, vals):
        res = super(model_instruction, self).create(vals)
        res.seq = self.env["ir.sequence"].next_by_code("actioninstruction")
        return res
