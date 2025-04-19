
{
    'name': 'helpdesk  & crm custom ',
    'version': '1.3',
    'category': 'helpdesk',
    'description': """create sales order from ticket  and relate between ticket and lead 
""",
    'depends': ['crm', 'helpdesk','crm_helpdesk','sale','base_setup',
        'sales_team',
        'mail','social',
        'calendar',
        'resource',
        'project',
        'utm',
        'sale_crm',
        'web_tour',
        'contacts',
        'digest',
        'hr_expense',
                'sales_team',
                'event','quality_control',
        'phone_validation',
                # 'dan_adj'
                ],
    # 'data': ['views/ticket_sale.xml','views/survey_sheet.xml','secuirty/ir.model.access.csv',
    #          'views/menus.xml','views/surevy_sheet_report.xml',"views/sale_order.xml","views/quality.xml"],
    'data' : ['views/lead.xml',
              'views/sale_order.xml',
              'views/tickets.xml',
              ],
     
    'installable': True,
    'auto_install': True,
}
