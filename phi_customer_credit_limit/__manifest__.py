# -*- coding: utf-8 -*-
{
    'name': "Phidias : Customer Credit Limit",

    'summary': """
        Phidias : Customer Credit Limit
        """,

    'description': """
        Phidias : Customer Credit Limit
    """,

    'author': "Phidias",
    'website': "http://www.phidias.fr",
    'category': 'Uncategorized',
    'version': '15.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale_management',
        'account',
    ],
    "data": [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/sale_order_view.xml',
        'views/partner_view.xml',
        'wizard/customer_limit_wizard_view.xml',
    ]
}
