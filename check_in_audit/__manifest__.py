{
    'name': "check in Audit",
    'author': '',
    'category': 'hr',
    'summary': """""",
    'description': """
""",
    'depends': ['base', 'hr','hr_attendance',
                'dan_adj'
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee.xml',
        'wizard/attendance_audit.xml',
    ],
    # omar
    # 'assets': {
    #     'web.assets_backend': [
    #         ('replace', 'hr_attendance/static/src/js/my_attendances.js',
    #          'check_in_audit/static/src/js/my_attendances.js'),
    #     ]},
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
