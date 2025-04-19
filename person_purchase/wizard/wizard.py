from odoo import api, fields, models


class PeriodicalReportProduct(models.TransientModel):
    _name = "person.data"

    creation_date = fields.Date(string='creation data')

    # competitor_id = fields.Many2one('res.competitor', string='Competitor')
    sale_order_id = fields.Many2one('sale.order',"Sale order")
    price_list = fields.Many2one('product.pricelist',"Price List")

    def check_report(self):
        list = []
        # for rec in self.competitor_id:
        #     list.append(rec.id)
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'creation_date':self.creation_date,

                'sale_order_id':self.sale_order_id.id,
                'price_list':self.price_list.id


            },
        }
        return self.env.ref('person_purchase.action_purchase_person_report').report_action(self, data=data)
