# -*- coding: utf-8 -*-
{
    'name': "Phidias : Order Comment",

    'summary': """
        Phidias : Order comment
        """,

    'description': """
        Phidias : order comment
    """,

    'author': "Phidias",
    'website': "http://www.phidias.fr",
    'category': 'Uncategorized',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'sale_management',
        'account',
        'stock',
    ],
    "data": [
        'views/sale_order_view.xml',
        'views/account_move.xml',
        'views/stock_picking_views.xml',
    ]
}
