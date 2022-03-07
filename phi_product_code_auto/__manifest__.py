# -*- coding: utf-8 -*-
{
    'name': "Phidias : Product Code Auto",

    'summary': """
        Phidias : Product Code Auto
        """,

    'description': """
        Phidias :Product Code Auto
    """,

    'author': "Phidias",
    'website': "http://www.phidias.fr",
    'category': 'Uncategorized',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'product',
    ],
    "data": [
        'views/product_attribute_views.xml',
        'views/product_views.xml',
        'views/product_category.xml',
        'data/sequence.xml',
    ]
}
