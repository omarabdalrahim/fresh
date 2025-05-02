from odoo import  models,api,fields

class MRP(models.TransientModel):
    _inherit = 'mrp.immediate.production'

    def process(self):
        res = super(MRP, self).process()
        print("in mrp validation")
        for mo in self.mo_ids:
            for check in mo.check_ids:
                print('---->', mo.product_qty)
                check.qty = mo.product_qty
                moveslist=[]
                for move in mo.move_raw_ids:
                    moveslist.append((0, 0, {
                        'product_id':move.product_id.id,
                        'name':move.name,
                        'location_dest_id':move.location_dest_id.id,
                        'location_id': move.location_id.id,
                        'product_uom_qty': move.product_uom_qty,
                        'product_uom': move.product_uom.id,
                        'quantity_done': move.quantity_done,
                        'check_id':check.id,
                    }) )
                print('----=',moveslist)
                check.move_raw_ids = moveslist
        return res
