from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz
from collections import OrderedDict

_logger = logging.getLogger(__name__)
from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request
from collections import OrderedDict
from datetime import datetime
import itertools

class ReportProductSale(models.AbstractModel):
    _name = "report.prepared_product_so.report_saleorder_prepared"

    @api.model
    def _get_report_values(self, docids, data=None):

        sales_order = self.env['sale.order'].search([('id','in',docids)])
        product_list =[]
        for rec in sales_order.order_line:
            if 13 in rec.product_id.public_categ_ids.ids :
                if rec.product_id.bom_ids:
                    product_list.append({'product_id':rec.product_id,'qty':rec.product_uom_qty,'pro_id':rec.product_id.id})
        lines = sorted(product_list, key=lambda i: (i['pro_id']))
        lst=[]

        for key, group in itertools.groupby(lines, key=lambda x: (x['pro_id'])):

            quantity=0
            id=''

            for item in group:


                pro_name = item['product_id']
                quantity+= item['qty']
                id = item['pro_id']

            lst.append({'product_id': pro_name, "qty": quantity,'pro_id':id})
        product_list=[]
        for rec in lst:

            for pro in rec['product_id'].bom_ids:
                for l in pro.bom_line_ids:
                     product_list.append({'pro_id':l.product_id.id,'product_id':l.product_id,'qty':l.product_qty*rec['qty']})

        lines = sorted(product_list, key=lambda i: (i['pro_id']))
        res = []
        for key, group in itertools.groupby(lines, key=lambda x: (x['pro_id'])):

            quantity = 0
            for item in group:
                pro_name = item['product_id']
                quantity += item['qty']
            res.append({'product_id': pro_name, "qty": quantity})




        return {

             "lst":lst,
            "product_list":res

        }

