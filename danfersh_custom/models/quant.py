from odoo import fields, models, api


class Quant(models.Model):
    _inherit = 'stock.quant'
    def action_internal_note(self):
        lcation_id=''
        move_ids_without_package=[]
        for rec in self:
            print(">>>>>>>>",rec.location_id.warehouse_id)
            move_ids_without_package.append((0,0,{
                'product_id':rec.product_id.id,
                'product_uom_qty':rec.quantity,
                'name':rec.product_id.name,
                'product_uom':rec.product_uom_id.id
            }))
            lcation_id = rec.location_id
        view = self.env.ref('stock.view_picking_form')
        picking_id = self.env['stock.picking.type'].search([('warehouse_id','=',lcation_id.warehouse_id.id),\
                                                            ('code','=','internal')],limit=1)
        # move_ids_without_package
        return {
            'name': ('Internal Transfer'),
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'context': {'default_picking_type_id': picking_id.id, 'default_location_id': lcation_id.id,
                        'default_move_ids_without_package':move_ids_without_package},
            'target': 'current'
        }
