from odoo import fields, models, api


class Partner(models.Model):
    _name = 'res.partner.search'
    date = fields.Date()
    name = fields.Char(default='Contact Search Sales')
    result = fields.Html()
    partner_ids = fields.Many2many("res.partner", )

    def get_data(self):
        domain = []
        self.result = ''
        domain.append(('date_order', '=', self.date))
        if self.partner_ids:
            state_ids = []
            for rec in self.partner_ids:
                if rec.state_id:
                    state_ids.append((rec.state_id.id))

            for line in self.env['res.country.state'].search([('id','in',state_ids)]):
                # self.result = '\n'.join(["-" + line.name, self.result])
                count = len(self.env['res.partner'].search([('id','in',self.partner_ids.ids),('state_id', '=', line.id)]))
                for rec in self.env['res.partner'].search([('id','in',self.partner_ids.ids),('state_id', '=', line.id)]):

                    if not self.env['sale.order'].search(
                            [('x_customer_order_delivery_date', '=', self.date), ('partner_id', '=', rec.id)]):

                        if rec.name:
                            self.result = '\n'.join([str(count) + "-" + rec.name, self.result])
                            count -= 1
                self.result = '\n'.join(["-" + line.name, self.result])

        if not self.partner_ids:
            for line in self.env['res.country.state'].search([]):

                count = len(self.env['res.partner'].search([('state_id', '=', line.id)]))
                for rec in self.env['res.partner'].search([('state_id', '=', line.id)]):

                    if not self.env['sale.order'].search(
                            [('x_customer_order_delivery_date', '=', self.date), ('partner_id', '=', rec.id)]):

                        if rec.name:
                            self.result = '\n'.join([str(count)+"-" + rec.name, self.result])
                            count-=1
                self.result = '\n'.join(["-" + line.name, self.result])
