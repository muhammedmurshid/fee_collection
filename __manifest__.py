{
    'name': "Fee Collection",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['mail', 'base', 'logic_base','leads'],
    'data': [
        'security/ir.model.access.csv',
        'security/fee_collection_rules.xml',
        'views/fee_collection.xml',
        'views/admission_fee_template.xml',
        'views/course_fee.xml',
        'views/course_fee_template.xml',
    ],

    'summary': "logic_fee_collection",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}