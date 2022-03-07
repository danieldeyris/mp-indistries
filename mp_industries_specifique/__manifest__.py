# -*- coding: utf-8 -*-
{
    'name': "Phidias : specifique Mp Industries",

    'summary': """
        Phidias : specifique Mp Industries
        """,

    'description': """
        Phidias : specifique Mp Industries
    """,

    'author': "Phidias",
    'website': "http://www.phidias.fr",
    'category': 'Uncategorized',
    'version': '15.0.0.3',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': [
        'crm',
        'sale',
        'sale_management',
        'account',
        'stock',
        'purchase',
        'account_accountant',
        'mrp',
        'l10n_fr',
        'l10n_fr_reports',
        'l10n_fr_fec',
        'web_studio',
        'phi_order_mail_with_product_attachments',
        'phi_replenishment_vendor_default',
        'phi_product_code_auto',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'report/report_mrporder.xml',
        'report/report_invoice.xml',
        'report/stock_picking.xml',
        'report/report_purchase_order.xml',
    ]
}
