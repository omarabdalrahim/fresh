from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz
import itertools
_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.pricelist_pisonaj.pisonaj_sum_report"

    def _get_report_values(self, docids, data=None):
        docs_right, docs_left, docs = [], [], []
        pricelis = self.env['product.pricelist'].search([('id', 'in', docids)])
        i, j = 1, 1
        pages = []
        check = False

        product_cate = []
        for record in pricelis.item_ids:
            if record.product_tmpl_id:
                new_pro = record.product_tmpl_id
            elif record.product_id:
                new_pro = record.product_id.product_tmpl_id
            for rec in new_pro.public_categ_ids:
                if rec not in product_cate and rec:
                    product_cate.append(rec)

        cate_id = []
        pages.append(j)
        items = self.env['product.pricelist.item'].search([('pricelist_id', 'in', pricelis.ids)],
                                                          order="product_tmpl_id asc")
        docs=[]
        col=1
        lines,pages=[],[]
        print("public",pricelis)
        page=1
        for record in product_cate:
            row_check=False
            col=1
            row=1
            cate_id.append({'cate_id':record,'page':page})
            for rec in items:
                    new_pro_add=''
                    if rec.product_tmpl_id:
                        new_pro_add = rec.product_tmpl_id
                    elif rec.product_id:
                        new_pro_add = rec.product_id.product_tmpl_id
                    if    new_pro_add and new_pro_add.is_published==True and record.id in  new_pro_add.public_categ_ids.ids :


                            docs.append({'row': row, 'categ_id': record, 'product_name': new_pro_add.name,
                                         'pro_id': new_pro_add,
                                         'product_tmpl_id': new_pro_add.name,

                                         'fixed_price': rec.price, 'check': False,'page':page})

                            if col==5:
                                row+=1
                                col=0
                            if row==5:
                                page+=1
                                row=1
                                cate_id.append({'cate_id': record, 'page': page})

                            col+=1

            page+=1

        docs = sorted(docs, key=lambda i: (i['row']))

        lst=[]
        i=0
        for key, group in itertools.groupby(docs, key=lambda x: (x['row'],x['categ_id'])):

            line=[]

            for item in group:

               line.append({'row': item['row'], 'categ_id': item['categ_id'], 'product_name': item['product_name'],
                             'pro_id':item['pro_id'],
                             'product_tmpl_id':item['product_tmpl_id'],
                             'fixed_price': item['fixed_price'],'page':item['page']})
            i+=1
            if line :
                lst.append({'categ_id':key[1],'line':line})













        website_logo = []
        if len(pricelis) == 1:
            website_logo = pricelis.website_id
        height_field = 1
        height = []

        cate_id = sorted(cate_id, key=lambda i: i['cate_id'])



        return {
            # 'doc_ids': docs.ids,
            'doc_model': 'product.pricelist',

            'docs': lst,
            'height_field': height_field,
            'check': check,
            'pages': pages,
            'website_logo': website_logo,
            'product_cate': product_cate,
            'cate_id': cate_id,
            'proforma': True
        }
