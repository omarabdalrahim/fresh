# -*- coding: utf-8 -*-
{
    'name': "Attendance Sheet Print",

    'summary': """
        Print Attendance Sheet""",

    'description': """
        Print Attendance Sheet
    """,

    'author': "Enas yasser",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','rm_hr_attendance_sheet'],

    # always loaded
    'data': [
        'views/attendance_sheet_report.xml',
    ],
    # only loaded in demonstration mode

}
