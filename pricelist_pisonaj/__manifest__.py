
{
    'name': 'Invoice Sum Quantity',
    'version': '1.3',
    'category': 'account',
    'description': """
Sum quantity of some of invoice line
===================================================
""",
    'depends': ['sale','product','product_purchase'],



    'data': ['views/report_action.xml','views/config.xml','views/item_price.xml','views/pricelist_2.xml','views/tempalet_price_list.xml'],
     
    'installable': True,
    'auto_install': True,
}
