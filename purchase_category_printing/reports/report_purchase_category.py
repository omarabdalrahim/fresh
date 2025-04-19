import math

from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ReportProductSale(models.AbstractModel):
    _name = "report.purchase_category_printing.report_purchase_category"

    @api.model
    def _get_report_values(self, docids, data=None):

        order = self.env['purchase.order'].search([('id','in',docids)])
        docs = self.env['purchase.order'].browse(self.env.context.get('active_id'))
        categ_id,product_ids,no_categ_pro,categ_id_list =[],[],[],[]
        for rec in order.order_line:

            if rec.product_id.public_categ_ids:
            # for categ in  rec.product_id.public_categ_ids:

                if rec.product_id.public_categ_ids[0] not in categ_id_list:
                         categ_id.append({'categ':rec.product_id.public_categ_ids[0],'order':rec.order_id})
                         categ_id_list.append(rec.product_id.public_categ_ids[0])
                #rec.product_template_id.name
            price_unit = 0
            product_price = ''
            product_price = self.env['purchase.order.line'].search(
                [('product_id', '=', rec.product_id.id), ('price_unit', '>', 0),('order_id','!=',rec.order_id.id)], order='create_date desc',
                limit=1)
            product_price_purchase = self.env['person.purchase.line'].search(
                [('product_id', '=', rec.product_id.id), ('purchase_price', '>', 0)],
                order='create_date desc', limit=1)
            if  product_price_purchase and product_price:
                if product_price_purchase.create_date > product_price.create_date and product_price_purchase.purchase_price > 0:
                    price_unit = product_price_purchase.purchase_price
            elif product_price.price_unit > 0 and price_unit ==0:
                price_unit = product_price.price_unit
            elif product_price_purchase.purchase_price > 0 and price_unit ==0:
                price_unit = product_price_purchase.purchase_price
            y = price_unit - math.floor(price_unit)
            y = round(y, 2)
            if y > 0 and y < 0.25:
                y = 0.25
            elif y > 0.25 and y <= 0.5:
                y = 0.5
            elif y > 0.5 and y <= 0.75:
                y = 0.75
            elif y > 0.75:
                y = 1
            price_unit = math.floor(price_unit) + y
            total = round(rec.price_total,2)
            subtotal = round(rec.price_total,2)
            if rec.order_id.discount_print >0:
                price_unit =price_unit - (price_unit*(rec.order_id.discount_print)/100)
                total = rec.price_total - (rec.price_total*(rec.order_id.discount_print)/100)
                subtotal = rec.price_total - (rec.price_total*(rec.order_id.discount_print)/100)

            total = round(total, 2)
            subtotal = round(subtotal, 2)
            #rec.product_template_id.name
            if   rec.product_id.public_categ_ids:

                product_ids.append({'product_id':rec.name,'price_unit':price_unit,'product_qty':str(rec.product_qty)+rec.product_uom.name,
                                    'price_subtotal': subtotal,'total':total,'categ_id':rec.product_id.public_categ_ids[0]
                                    })
            else:
                no_categ_pro.append({'product_id':rec.name, 'price_unit': price_unit,
                                    'product_qty': str(rec.product_qty) + rec.product_uom.name,
                                    'price_subtotal': subtotal,'order':rec.order_id,'total':total,
                                    })




        return {

            "doc_model": 'purchase.order',
            'no_categ_pro' :no_categ_pro,
            'product_ids':product_ids,
            'categ_id':categ_id,
            'order':order,
            'docs':docs


        }