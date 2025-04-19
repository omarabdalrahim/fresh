{
    'name': "Dan Adj",
    'author': '',
    'category': 'Sales',
    'summary': """""",
    'description': """
""",

    'depends': ['base', 'sale', 'account', 'stock','website_sale','website_dan_custom','maintenance','mrp'],
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/templates.xml',
        'views/sale_order_view.xml',
        'views/transfer_wizard.xml',
        'views/audit.xml',
        'views/training.xml',
        'views/quilty.xml',
        'data/corn_job.xml',
        'data/data.xml',
        'reports/company_paper.xml',
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
