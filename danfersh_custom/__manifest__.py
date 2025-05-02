# -*- coding: utf-8 -*-
{
    'name': "danfersh_custom",

    'summary': """
        -add journal at partner to related any your invoice
        - print last purchase price from each product from stock.picking
        - add sign by customer at all tranasfer
        -add type at partner two confirm transfer after confirm ordder or confirm transfer and invoice
        - add receipt date at purchase order report 
        - add some of fields at sale order to calculate payment,and invoice amount 
        -add states field (transfer-invoice-payment) at sale order
        -add tax and discount at contact reflect at sales order when create order
        -add sales Template at contact and add related at sales order
        -print invoice from sales order
        -internal transfer from current stock at location (as server action)
        -internal transfer from Picking stock at location (as server action)
        -استبيان الزوار
        
        
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "MOHANED ABDELRHMAN",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','stock','quality','purchase','l10n_eg_edi_eta','hr_expense','mrp_account_enterprise','hr','hr_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
         'views/views.xml',
         'views/templates.xml',
         'views/templated-stock.xml',
        'wizard/wizard.xml',
        'wizard/report_partaner.xml',
        'wizard/template.xml',
        'views/purchase_order.xml',
        'views/invoice_sales_order.xml',
        'views/stock_quant.xml',
        'views/sale.xml',
        'views/mrp.xml',
        'views/hr_payslip.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
