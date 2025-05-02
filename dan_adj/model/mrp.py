from odoo import fields, models, api
import itertools
from collections import defaultdict

class StockMove(models.Model):
    _inherit = 'stock.move'
    check_id = fields.Many2one('quality.check')

    # def _create_quality_checks(self):
    #     # Groupby move by picking. Use it in order to generate missing quality checks.
    #     pick_moves = defaultdict(lambda: self.env['stock.move'])
    #     for move in self:
    #         if move.picking_id:
    #             pick_moves[move.picking_id] |= move
    #     check_vals_list = self._create_operation_quality_checks(pick_moves)
    #     # for picking, moves in pick_moves.items():
    #     #     # Quality checks by product
    #     #     quality_points_domain = self.env['quality.point']._get_domain(moves.product_id, picking.picking_type_id,
    #     #                                                                   measure_on='product')
    #     #     quality_points = self.env['quality.point'].sudo().search(quality_points_domain)
    #     #
    #     #     if not quality_points:
    #     #         continue
    #     #     picking_check_vals_list = quality_points._get_checks_values(moves.product_id, picking.company_id.id,
    #     #                                                                 existing_checks=picking.sudo().check_ids)
    #     #     for check_value in picking_check_vals_list:
    #     #         check_value.update({
    #     #             'picking_id': picking.id,
    #     #         })
    #     #     check_vals_list += picking_check_vals_list
    #     self.env['quality.check'].sudo().create(check_vals_list)

