
from odoo import api, models
from dateutil.relativedelta import relativedelta
import datetime
import logging
import pytz
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class ReportProductSale(models.AbstractModel):
    _name = "report.person_purchase.purchase_report_xlx"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        report_name = 'Purchase'

        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({'bold': True, 'border': 7, 'bg_color': '#6F856D', 'align': 'center'})
        unborder = workbook.add_format({'border': 0, })
        myprice = workbook.add_format({'bold': True, 'border': 7, 'bg_color': '#FFC300', 'align': 'center'})
        break_line = workbook.add_format({'bold': False, 'border': 7, 'bg_color': 'blue', 'align': 'center'})
        unbold = workbook.add_format({'bold': False, 'border': 7, 'align': 'center'})
        green = workbook.add_format({'bold': False, 'border': 7, 'align': 'center','bg_color':'green'})
        red = workbook.add_format({'bold': False, 'border': 7, 'align': 'center','bg_color':'red'})
        datetime_style = workbook.add_format(
            {'text_wrap': True, 'border': 7, 'num_format': 'dd-mm-yyyy', 'align': 'center'})


        row = 2
        col = 2
        creation_date = data["form"]["creation_date"]

        sale_order_id = data["form"]["sale_order_id"]
        price_list = data["form"]["price_list"]
        domain = []
        dates = []

        # if creation_date:
        #     domain.append(('creation_date', '=', creation_date))

        lines = self.env['person.purchase.line'].search(domain, order='product_id asc')
        comp_lines = []
        competitor_ids = []






        lst = []
        pro_list = []
        price_lst = self.env['product.pricelist.item'].search([('pricelist_id', '=', price_list)])
        i=4




        #lines = self.env['person.purchase.line'].search([('id', 'in', comp_lines)], order='product_id asc')
        # product_ids = []
        # for comp_id in lines:
        #     if competitor_id and comp_id.person_competitor_id.competitor_id.id == competitor_id:
        #         if comp_id.product_id not in product_ids:
        #            product_ids.append(comp_id.product_id)
        #     elif not competitor_id:
        #         if comp_id.product_id not in product_ids:
        #             product_ids.append(comp_id.product_id)



        i,j,k=2,3,4
        col=0
        # sheet.write(1, 2, 'Date', bold)
        sheet.write(1, 3, 'Product', bold)
        sheet.write(1, 4, 'Purchase Price', bold)
        sheet.write(1, 5, 'Sale Price', bold)
        sheet.write(1, 6, 'Diff', bold)
        sheet.write(1, 7, 'Diff %', bold)


        for prod in lines:
            old_timezone = pytz.timezone("UTC")
            new_timezone = pytz.timezone("Africa/Cairo")
            last_new_timezone = old_timezone.localize(prod.create_date).astimezone(new_timezone)
            last_new_timezone = last_new_timezone.strftime('%Y-%m-%d')
            last_new_timezone = datetime.datetime.strptime(last_new_timezone, '%Y-%m-%d')
            if creation_date == last_new_timezone.strftime('%Y-%m-%d'):
                print(">>>>>>>>>>>>>>>>>>>>>>>>>")
                my_price=0

                sheet.write(i, j, prod.product_id.name, unbold)
                j += 1
                sheet.write(i, j, prod.purchase_price, unbold)
                j += 1

                price_lst = self.env['product.pricelist.item'].search([('pricelist_id', '=', price_list)])
                for plt in price_lst:

                    if plt.product_id.id==prod.id and plt.product_id:
                        my_price=float(plt.price[1:])


                    elif plt.product_tmpl_id and plt.product_tmpl_id.id==prod.product_id.product_tmpl_id.id:
                        my_price= float(plt.price[1:])
                sheet.write(i, j, my_price, myprice)
                j += 1
                print(">>>>>>>>>>>>>>>",myprice)
                dif = my_price - prod.purchase_price
                if dif <0:
                    sheet.write(i, j, dif, green)
                    j += 1
                    sheet.write(i, j, dif/100, green)
                else:
                    sheet.write(i, j, dif, red)
                    j += 1
                    sheet.write(i, j, dif/100, red)
                j += 1


                j=3
                i += 1


