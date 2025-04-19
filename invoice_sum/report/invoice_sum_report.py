from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz
import operator
from collections import OrderedDict
from collections import OrderedDict
_logger = logging.getLogger(__name__)
import itertools

class ReportProductSale(models.AbstractModel):
    _name = "report.invoice_sum.invoice_sum_report"

    def _get_report_values(self, docids, data=None):
        #print("get_reprort incoive ++++++++++++++++++++++++++++")
        move =self.env['account.move'].search([('id','in',docids)])
        docs=[]

        cst_list=[]

        for record in move.invoice_line_ids:
            docs.append({'move_id': record.move_id, 'product_id': record.product_id, 'price_unit': record.price_unit,
                         'quantity': record.quantity,'name':record.product_id.name,'name':record.product_id.name
                            , "tax_ids": record.tax_ids, "price_total": record.price_subtotal, 'check': False})



        docs_list = []
        docs=sorted(docs, key=lambda i: (i['name'],i['price_unit']))
        print(docs)

        for key, group in itertools.groupby( docs, key=lambda x: (x['product_id'], x['price_unit'])):

            price_total,quantity,i,j=0,0,0,0
            lst={}
            print(key)
            print(group)
            for item in group:
                price_total += item["price_total"]
                quantity += item["quantity"]
                lst= {'move_id': item["move_id"], 'product_id': item["product_id"], 'price_unit': item["price_unit"],
                     'quantity': quantity
                        , "tax_ids": item["tax_ids"], "price_total": price_total, 'check': False}



            if lst:
                docs_list.append(lst)












        return {
            # 'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs_list,
            'cst_list':cst_list,
            'move':move,

            'proforma': True
        }
    def search_docs(self, docs, product_id,move_id):
            check=False
            if len(docs)==0:
                print("first")
                return False
            else:
               for item in docs:
                    print(item)
                    print(item['product_id'])

                    if item["product_id"] == product_id and item['move_id']==move_id:
                        check=True
                        return True
               if check==False:
                        return False



