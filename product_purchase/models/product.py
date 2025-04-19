from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.product'
    puchase_price= fields.Float("Price of Purchase ",compute='_get_last_purchase_price',store=False)
    type_cal= fields.Selection([('Cost','Cost'),('Purchase Price','Purchase Price')],'Type',default='Cost')
    amount_list= fields.Selection([('Precentage','Precentage'),('Amount','Amount')],'Type')
    amount= fields.Float("Amount")
    precentage= fields.Float("Precentage")
    update_price = fields.Float("Update Purchase price")

    @api.depends('purchased_product_qty','update_price')
    def _get_last_purchase_price(self):
        for product in self:
            print(product.name)
            # manu_orer  = self.env[''].search([])
            purchase_order_line = self.env['purchase.order.line'].search([('partner_id','=',2908),('state','=','purchase'),('product_id','=',product.id)],order ='write_date desc')
            bom =self.env['mrp.bom'].search([('product_id','=',product.id)],order='write_date desc', limit=1)
            if not bom:
                bom = self.env['mrp.bom'].search([('product_tmpl_id', '=', product.product_tmpl_id.id)],order='write_date desc', limit=1)

            if bom :
                pur_price=0
                print(product.name)
                print(bom.bom_line_ids)
                for record in bom.bom_line_ids:
                    po = self.env['purchase.order.line'].search(
                        [('partner_id','=',2908),('state', '=', 'purchase'), ('product_id', '=', record.product_id.id)],
                        order='write_date desc', limit=1)

                    pur_price += (po.price_unit * record.product_qty)

                if pur_price>0 :
                        product.puchase_price =pur_price
                        return




            if product.update_price > 0:
                print("up", product.update_price)
                product.puchase_price = product.update_price

            elif purchase_order_line:

               product.puchase_price=purchase_order_line[0].price_unit
            else:
               product.puchase_price=0



    @api.depends('list_price', 'price_extra',"type_cal","precentage","amount","puchase_price")
    @api.depends_context('uom')
    def _compute_product_lst_price(self):
        to_uom = None
        if 'uom' in self._context:
            to_uom = self.env['uom.uom'].browse(self._context['uom'])

        for product in self:

            if to_uom:
                list_price = product.uom_id._compute_price(product.list_price, to_uom)
            else:
                list_price = product.list_price
            product.lst_price = list_price + product.price_extra
            if product.type_cal == 'Purchase Price' and product.amount_list == 'Precentage':
                prod_purchase = 0
                if product.puchase_price:
                    prod_purchase=product.puchase_price


                product.lst_price = ((prod_purchase * product.precentage) / 100) + prod_purchase
                product.list_price = product.lst_price
            elif product.type_cal == 'Purchase Price' and product.amount_list == 'Amount':
                prod_purchase = 0
                if product.puchase_price:
                    prod_purchase = product.puchase_price
                print("puchase_price", prod_purchase)
                product.lst_price = prod_purchase + product.amount
                product.list_price= product.lst_price
    # @api.onchange("type_cal","precentage","amount","puchase_price")
    # def update_l_price(self):
    #     print("onchange")
    #     if self.type_cal == 'Purchase Price' and self.amount_list == 'Precentage':
    #         print("puchase_price",self.puchase_price)
    #
    #         self.lst_price = ((self.puchase_price * self.precentage) / 100) + self.puchase_price
    #
    #
    #     if self.type_cal == 'Purchase Price' and self.amount_list == 'Amount':
    #         print("puchase_price", self.puchase_price)
    #         self.lst_price = self.puchase_price + self.amount
    #     print("list" ,self.lst_price)

    # def write(self, values):
    #
    #
    #     lst_price=0
    #     puchase_price=self.puchase_price
    #     if self.type_cal == 'Purchase Price' and self.amount_list == 'Precentage':
    #
    #         lst_price = ((puchase_price * self.precentage) / 100) + puchase_price
    #
    #
    #     if self.type_cal == 'Purchase Price' and self.amount_list == 'Amount':
    #         lst_price = puchase_price + self.amount
    #     if lst_price !=0:
    #         values['lst_price']= lst_price
    #
    #
    #     return super(ProductTemplate, self).write(values)






    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}

    def update_purchase_order(self):
        view = self.env.ref('product_purchase.product_template_purchase_price_update')
        print("Id", self.id)
        print({'default_res_id': self.id})
        return {
            'name': _('Update Purchase Price'),
            'view_type': 'form',
            "view_mode": 'form',
            'view_id': view.id,
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new'
        }