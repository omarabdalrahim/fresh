from odoo import fields, models, api
from dateutil.relativedelta import relativedelta

class AccountRegisterPAyrol(models.TransientModel):
    _name ="account.payment.register.payslip"
    journal_paid_id = fields.Many2one("account.journal", domain="[('type','in',('cash','bank'))]")

    def create_paid(self):
        for rec in self.env['hr.payslip'].browse(self._context.get('active_ids', [])):
            amount = rec.line_ids[-1].amount
            amount = rec.net_wage
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>44444>>>>>>.",amount)
            if rec.state=='done':
                rec.payment_move_id = self.env['account.move'].sudo().create(

                    ({
                        'partner_id': '',
                        'journal_id': self.journal_paid_id.id,
                        'ref': rec.name,
                        'line_ids': [(0, 0, {
                            'name': rec.name,
                            'account_id': self.journal_paid_id.default_account_id.id,
                            'credit': amount,
                            'debit': 0
                        }), (0, 0, {
                            'name':rec.name,
                            'account_id': self.env['account.account'].search([('code', '=', '2104')]).id,
                            'credit': 0,
                            'debit': amount
                        }),
                                     ]
                    })
                )
                rec.payment_move_id.sudo().action_post()
                rec.action_payslip_paid()


class Payslip(models.Model):
    _inherit = "hr.payslip"
    salary_amount = fields.Float()
    service_amount = fields.Float()
    leave_amount = fields.Float()
    invoice_amount = fields.Float()
    expense_amount = fields.Float()
    sales_amount = fields.Float()
    journal_paid_id = fields.Many2one("account.journal",domain="[('type','in',('cash','bank'))]")
    payment_move_id = fields.Many2one("account.move",readonly=True)
    def print_sign(self):
        print(">>>>>>>>>>>>>.",self)
        return self.env.ref(
            'hr_payroll.action_report_payslip'
        ).report_action(self)



    def confirm_print(self):
        return {
            'name': ('Sign'),
            'res_model': 'hr.payslip',
            'view_mode': 'form',
            'model':'hr.payslip',
            'target': 'new',
            'res_id':self.id,
            'view_id': self.env.ref('danfersh_custom.hr_payslip_payment_view_form_sign').id,
            'type': 'ir.actions.act_window',
        }

    def action_register_payment(self):
        view = self.env.ref('danfersh_custom.hr_payslip_payment_view_form')


        return {
            'name': ('Register Payment'),
            'res_model': 'account.payment.register.payslip',
            'view_mode': 'form',
            'context': {
                'active_model': 'hr.payslip',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }



    def compute_sheet(self):
        for rec in self:
            rec.salary_amount = 0
            rec.leave_amount = 0
            rec.invoice_amount = 0
            rec.sales_amount=0
            if rec.date_to and rec.date_from and rec.contract_id:
                duration = rec.date_to - rec.date_from
                # rec.salary_amount = round(((rec.contract_id.wage/30)*(duration.days)),2)
                day_salary = (rec.contract_id.wage / 30)

                rec.salary_amount = (duration.days + 1) * day_salary
                if rec.salary_amount>rec.contract_id.wage:
                    rec.salary_amount = rec.contract_id.wage


                difference_in_years = relativedelta(rec.date_from, rec.employee_id.x_hiring_date).years

                if difference_in_years < 5:
                    rec.service_amount = ((rec.salary_amount / 12) * 6) / 12
                if difference_in_years >= 5:
                    rec.service_amount = (((rec.salary_amount / 12) * 6) / 12) * 2
                leave_ids = self.env['hr.leave'].search(
                    [('request_date_from', '>=', rec.date_from), ('holiday_status_id.unpaid', '=', True),
                     ('request_date_to', '<=', rec.date_to), \
                     ('employee_id', '=', rec.employee_id.id), ('state', '=', 'validate')])

                if leave_ids:

                    rec.leave_amount = sum(leave_ids.mapped('number_of_days')) * day_salary
                else:
                    rec.leave_amount = 0
                if rec.employee_id.address_home_id:
                    invoice_ids = self.env['account.move'].search(
                        [('partner_id', '=', rec.employee_id.address_home_id.id), ('state', '=', 'posted'),
                         ('payment_state', '!=', 'paid')])
                    rec.invoice_amount = sum(invoice_ids.mapped('amount_residual'))
                expense_ids = self.env['hr.expense'].search(
                    [('date', '>=', rec.date_from), ('state', 'in', ('approved', 'done')),
                     ('date', '<=', rec.date_to), \
                     ('employee_id', '=', rec.employee_id.id), ])
                rec.expense_amount = sum(expense_ids.mapped('total_amount'))
            warehouse_id = self.env['stock.warehouse'].search([('x_employee_id', '=', rec.employee_id.id)],limit=1)

            if warehouse_id:
                self.env.cr.execute("""
                select count(*)
                    from sale_order 
                    where state='done' and delivery_status='full' and warehouse_id=%s
                    and x_customer_order_delivery_date>='%s' 
                    and x_customer_order_delivery_date<='%s'
                    group by x_customer_order_delivery_date
                     
                    HAVING COUNT(*) > 20
                """%(warehouse_id.id,rec.date_from,rec.date_to))

                for sql in self.env.cr.fetchall():

                    rec.sales_amount +=sql[0]-20


        res = super(Payslip, self).compute_sheet()

        return res


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    amount = fields.Monetary(string='Amount', compute='_compute_amount', store=True, copy=True)

    @api.depends('is_paid', 'number_of_hours', 'number_of_days', 'payslip_id', 'contract_id.wage', 'code',
                 'payslip_id.sum_worked_hours')
    def _compute_amount(self):
        for worked_days in self:
            if worked_days.payslip_id.edited or worked_days.payslip_id.state not in ['draft', 'verify']:
                continue
            # if not worked_days.contract_id or worked_days.code == 'OUT':
            #     worked_days.amount = 0
            #     continue
            # if worked_days.payslip_id.contract_id.employee_id.resource_calendar_id.hours_per_day != 0:
            #     worked_days.amount = round((
            #             worked_days.payslip_id.contract_id.wage / 30 / worked_days.payslip_id.contract_id.employee_id.resource_calendar_id.hours_per_day),
            #         2)
            # else:
            #     worked_days.amount = 0
            # if worked_days.code in ('ATTSHAB', 'ATTSHLI', 'ATTSHDT'):
            #     worked_days.amount = worked_days.amount * -1
            if worked_days.number_of_days > 1:
                # round((
                #         worked_days.payslip_id.contract_id.wage / (
                #     (worked_days.payslip_id.date_to - worked_days.payslip_id.date_from).days)),
                #     2) * int(worked_days.number_of_days)
                day_value = worked_days.payslip_id.contract_id.wage / (30)
                worked_days.amount = day_value * int(worked_days.number_of_days)
            # else:
            #     worked_days.amount = round((
            #             worked_days.payslip_id.contract_id.wage / 30 / worked_days.payslip_id.contract_id.employee_id.resource_calendar_id.hours_per_day),
            #         2) * worked_days.number_of_hours
            if worked_days.code in ('ATTSHAB', 'ATTSHLI', 'ATTSHDT'):
                worked_days.amount = worked_days.amount * -1
