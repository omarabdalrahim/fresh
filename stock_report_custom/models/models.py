# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_report_custom(models.Model):
    _inherit ='stock.report'
    x_sales_person = fields.Many2one("res.users",string="Sales Person")
    sales_person = fields.Many2one("res.users",string="Sales Person")

    sale_id = fields.Many2one("sale.order",string="Sales Order")

    def _select(self):
        select_str = """
            sm.id as id,
            sp.name as picking_name,
            sp.date_done as date_done,
            sp.creation_date as creation_date,
            sp.scheduled_date as scheduled_date,
            sp.partner_id as partner_id,
            sp.is_backorder as is_backorder,
            sp.delay as delay,
            sp.delay > 0 as is_late,
            sp.cycle_time as cycle_time,
            spt.code as picking_type_code,
            spt.name as operation_type,
            p.id as product_id,
            sm.reference as reference,
            sm.picking_id as picking_id,
            sm.state as state,
            sm.product_qty as product_qty,
            sm.company_id as company_id,
            cat.id as categ_id,
            sp.user_id as x_sales_person,
            sp.user_id as sales_person,
            sp.sale_id as sale_id
        """

        return select_str

    def _from(self):
        from_str = """
            stock_move sm
            LEFT JOIN (
                SELECT
                    id,
                    name,
                    date_done,
                    date as creation_date,
                    scheduled_date,
                    partner_id,
                    user_id,
                    sale_id,
                    backorder_id IS NOT NULL as is_backorder,
                    (extract(epoch from avg(date_done-scheduled_date))/(24*60*60))::decimal(16,2) as delay,
                    (extract(epoch from avg(date_done-date))/(24*60*60))::decimal(16,2) as cycle_time
                FROM
                    stock_picking
                GROUP BY
                    id,
                    name,
                    date_done,
                    date,
                    scheduled_date,
                    partner_id,
                    is_backorder,user_id,sale_id
            ) sp ON sm.picking_id = sp.id
            LEFT JOIN stock_picking_type spt ON sm.picking_type_id = spt.id
            INNER JOIN product_product p ON sm.product_id = p.id
            INNER JOIN product_template t ON p.product_tmpl_id = t.id
            INNER JOIN product_category cat ON t.categ_id = cat.id
            WHERE t.type = 'product'
        """

        return from_str

    def _group_by(self):
        group_by_str = """
            sm.id,
            sm.reference,
            sm.picking_id,
            sm.state,
            sm.product_qty,
            sm.company_id,
            sp.name,
            sp.date_done,
            sp.creation_date,
            sp.scheduled_date,
            sp.partner_id,
            sp.is_backorder,
            sp.delay,
            sp.cycle_time,
            spt.code,
            spt.name,
            p.id,
            is_late,
            cat.id,
            sp.user_id,
            sp.sale_id
        """

        return group_by_str