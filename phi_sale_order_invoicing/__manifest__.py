# -*- coding: utf-8 -*-
{
    'name': "Phidias : Sale Order Invoicing",

    'summary': """
        Phidias : Sale Order Invoicing
        """,

    'description': """
        Phidias : Sale Order Invoicing
    """,

    'author': "Phidias",
    'website': "http://www.phidias.fr",
    'category': 'Uncategorized',
    'version': '14.0.0.4',

    # any module necessary for this one to work correctly
    'depends': [
        'sale',
        'account',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/partner_view.xml',
        'data/service_cron_data.xml',
        'views/invoicing_run.xml',
    ]
}
