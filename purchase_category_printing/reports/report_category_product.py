
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ReportProductSale(models.AbstractModel):
    _name = "report.purchase_category_printing.report_category_product"

    @api.model
    def _get_report_values(self, docids, data=None):
        print(">>>>>>",docids)
        products = self.env['product.template'].search([('id','in',docids)],order='name desc')
        docs = self.env['product.template'].browse(self.env.context.get('active_id'))
        product_list,categ_id_list,product_list_no=[],[],[]
        for rec in products:
            if rec.public_categ_ids:
                if rec.public_categ_ids[0] not in categ_id_list:

                    categ_id_list.append(rec.public_categ_ids[0])

            if rec.public_categ_ids:
                product_list.append({'product_id': rec.name, 'price_unit': rec.list_price,'pro_id':rec,
                                     'categ_id': rec.public_categ_ids[0]
                                     })
            else:
                product_list_no.append({'product_id': rec.name, 'price_unit': rec.list_price,'pro_id':rec,

                                     })







        return {

            "doc_model": 'purchase.order',
            'product_list':product_list,
            'categ_id_list':categ_id_list,
            'product_list_no':product_list_no,
            'docs':docs


        }

