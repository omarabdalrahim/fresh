from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, Command, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero, float_repr, float_compare, is_html_empty
from odoo.tools.misc import clean_context, format_date

class ExpenseReport(models.Model):
    _inherit = "hr.expense.sheet"
    @api.model
    def _default_bank_journal_id(self):
        raise ValidationError(self.env.user.x_expense_journal_id)
        company_journal_id = self.env.company.company_expense_journal_id
        if self.env.user.x_expense_journal_id:
            return self.env.user.x_expense_journal_id
        if company_journal_id:
            return company_journal_id
        default_company_id = self.default_get(['company_id'])['company_id']

        journal = self.env['account.journal'].search(
            [('type', 'in', ['cash', 'bank']), ('company_id', '=', default_company_id)], limit=1)
        return journal
class expense(models.Model):
    _inherit = "hr.expense"

    def _get_default_expense_sheet_values(self):
        # If there is an expense with total_amount_company == 0, it means that expense has not been processed by OCR yet
        expenses_with_amount = self.filtered(lambda expense: not float_compare(expense.total_amount_company, 0.0,
                                                                               precision_rounding=expense.company_currency_id.rounding) == 0)

        if any(expense.state != 'draft' or expense.sheet_id for expense in expenses_with_amount):
            raise UserError(_("You cannot report twice the same line!"))
        if not expenses_with_amount:
            raise UserError(_("You cannot report the expenses without amount!"))
        if len(expenses_with_amount.mapped('employee_id')) != 1:
            raise UserError(_("You cannot report expenses for different employees in the same report."))
        if any(not expense.product_id for expense in expenses_with_amount):
            raise UserError(_("You can not create report without category."))
        if len(self.company_id) != 1:
            raise UserError(_("You cannot report expenses for different companies in the same report."))

        # Check if two reports should be created
        own_expenses = expenses_with_amount.filtered(lambda x: x.payment_mode == 'own_account')
        company_expenses = expenses_with_amount - own_expenses
        create_two_reports = own_expenses and company_expenses

        sheets = [own_expenses, company_expenses] if create_two_reports else [expenses_with_amount]
        values = []
        for todo in sheets:
            if len(todo) == 1:
                expense_name = todo.name
            else:
                dates = todo.mapped('date')
                min_date = format_date(self.env, min(dates))
                max_date = format_date(self.env, max(dates))
                expense_name = min_date if max_date == min_date else "%s - %s" % (min_date, max_date)

            vals = {
                'company_id': self.company_id.id,
                'employee_id': self[0].employee_id.id,
                'name': expense_name,
                'expense_line_ids': [Command.set(todo.ids)],
                'state': 'draft',
                'bank_journal_id': self.env.user.x_expense_journal_id.id if  self.env.user.x_expense_journal_id else '',
            }
            values.append(vals)
        return values

