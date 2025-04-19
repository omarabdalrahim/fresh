import logging 
from odoo import fields, http, tools, _
from odoo.http import request
_logger = logging.getLogger(__name__)
from odoo import api, fields ,models
from odoo.exceptions import ValidationError 
from odoo.http import request
from collections import OrderedDict
from datetime import datetime
 
     
class order(models.Model):
    _inherit="sale.order"
  
    def action_purchase_order(self):
        whouse_id =self.env['stock.warehouse'].search([('defualt_warhouse','=',True)])
        lines=[]


        for rec in self:
            lines.append(rec.id)
        if whouse_id:
            return{ 'name':'Warehouse',
                'res_model': 'warehouse.sales',
                'target': 'new',
                 'view_type': 'form',
                 'view_mode': 'form',
                'view_id':self.env.ref('warehouse_at_salesorder.po_so_form2').id ,
                'context':{'default_sales_order':lines,'default_warehouse_id':whouse_id[0].id},
                'type': 'ir.actions.act_window', }
        else:
            return {'name': 'Warehouse',
                    'res_model': 'warehouse.sales',
                    'target': 'new',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': self.env.ref('warehouse_at_salesorder.po_so_form2').id,
                    'context': {'default_sales_order': lines},
                    'type': 'ir.actions.act_window',}