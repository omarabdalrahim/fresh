# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class x_deduction_allowance(models.Model):
#     _inherit = 'x_hr_loan'

    # @api.onchange('x_studio_many2one_field_TXy7X')
    # def _onchange_journal(self):
    #     if self.x_studio_many2one_field_TXy7X:
    #         self.x_studio_many2one_field_bOY5M=self.x_studio_many2one_field_TXy7X..id
    #


class bounce_penalites_loan_rule(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        loan = pen = bounce = 0
        for record in self:
            loan_id = self.env['x_hr_loan_line'].search(
                [('x_state', '=', 'approved_accounting'), ('x_employee_id', '=', record.employee_id.id) \
                    , ('x_date', '>=', record.date_from), ('x_date', '<=', record.date_to)])
            deduction_id = self.env['x_deduction_allowance_'].search(
                [('x_state', '=', 'approve'), ('x_type_value', '=', 'deduction') \
                    , ('x_employee_id', '=', record.employee_id.id) \
                    , ('x_date', '>=', record.date_from),
                 ('x_date', '<=', record.date_to)])
            bounce_id = self.env['x_deduction_allowance_'].search(
                [('x_state', '=', 'approve'), ('x_type_value', '=', 'allowance') \
                    , ('x_employee_id', '=', record.employee_id.id) \
                    , ('x_date', '>=', record.date_from),
                 ('x_date', '<=', record.date_to)])

            print(">>>>>>>>>>>>>>>>>>>", loan_id)
            for rec in loan_id:
                loan += rec.x_amount
            for rec in deduction_id:
                if rec.x_select_type == 'Day':
                    pen += (record.contract_id.wage / 30) * rec.x_mount
                elif rec.x_select_type == 'Fixed':
                    pen += rec.x_mount
            for rec in bounce_id:
                if rec.x_select_type == 'Day':
                    bounce += (record.contract_id.wage / 30) * rec.x_mount
                elif rec.x_select_type == 'Fixed':
                    bounce += rec.x_mount
            record.x_loan = loan
            record.x_penalty = pen
            record.x_bounce = bounce

        res=super(bounce_penalites_loan_rule, self).compute_sheet()

        return res

