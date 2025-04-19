
{
    'name': 'wrehoouse  from So   ',
    'version': '1.3',
    'category': 'sale',
    'description': """create purchase order according to some of sales order
""",
    'depends': ['sale','base','stock','website_sale'],
    'data': ["views/sales_order_view.xml",
             "views/template.xml",
             "security/ir.model.access.csv"],
    'installable': True,
    'auto_install': True,
}
