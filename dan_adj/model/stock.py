from odoo import fields, models, api

import itertools
class ModelName(models.Model):
    _inherit = 'stock.picking'


    def create_internal_transfer_action(self):
        move_lines=[]
        for i in self.env.context['active_ids']:
            transfer= self.env['stock.picking'].browse(i)
            for m in transfer.move_ids_without_package:
                print('sssss')
                move_lines.append({
                    'product_id':m.product_id.id,
                    'name':m.name,
                    'location_dest_id':m.location_dest_id.id,
                    'location_id':m.location_id.id,
                    'product_packaging_id':m.product_packaging_id.id,
                    'product_uom_qty':m.product_uom_qty,
                    'product_uom':m.product_uom.id,
                })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'transfer.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'move_lines': move_lines}
        }

class TransferWizard(models.TransientModel):
    _name='transfer.wizard'

    picking_type_id = fields.Many2one('stock.picking.type', string='Operation Type',required=True)
    company_id = fields.Many2one('res.company',default=lambda self: self.env.company)
    location_id = fields.Many2one(
        'stock.location', 'Source Location',
        domain="[('usage','=','internal'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        check_company=True,
        required=True,)
    location_dest_id = fields.Many2one(
        'stock.location', 'Destination Location',
        auto_join=True, index=True, required=True,
        check_company=True,)

    def create_transfer(self):
        moves= self._context["move_lines"]
        for m in moves:
            m['location_dest_id']=self.location_dest_id.id
            m['location_id']=self.location_id.id
        rec = self.env['stock.picking'].create({
            'picking_type_id':self.picking_type_id.id,
            'company_id':self.company_id.id,
            'location_id':self.location_id.id,
            'location_dest_id':self.location_dest_id.id,
            'move_ids_without_package':moves
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Transfer',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('id', '=', rec.id)],
            'context': "{'create': False}"
        }