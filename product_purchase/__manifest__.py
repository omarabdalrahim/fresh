
{
    'name': 'Product price  depends at purchase order   ',
    'version': '1.3',
    'category': 'sale',
    'description': """get product price depends at purchase order
""",
    'depends': ['sale','purchase'],
    'data': ["views/product_form.xml","views/price_item.xml"],
    'installable': True,
    'auto_install': True,
}
