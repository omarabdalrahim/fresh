# -*- coding: utf-8 -*-
{
    'name': "qualtiy_dan",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
      استبيان الزوار 
      تكويد النموذج والاجراء
    """,

    'author': "MOHAMED ABDELRHMAN",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','quality_control',
                'dan_adj'
                ],

    # always loaded
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/visitor.xml',
        'views/purpose.xml',
        'views/menu_action_codeing.xml',
        'views/quality.xml',
        'views/coding.xml',
        'views/menu_action_band.xml',
        'views/action_bands.xml',
        'views/page_action_first.xml',
        'views/revision.xml',
        'views/instruction.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
