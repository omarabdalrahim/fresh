
{
    'name': 'Purchase order  from So   ',
    'version': '1.3',
    'category': 'sale',
    'description': """create purchase order according to some of sales order
""",
    'depends': ['sale','warehouse_at_salesorder'],
    'data': ["views/order_form.xml"],
    'installable': True,
    'auto_install': True,
}
