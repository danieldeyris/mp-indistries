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
    'version': '15.0.0.19',
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
        'catalog_pricelist_report',
        'phi_customer_credit_limit',
        'phi_order_comment',
        'delivery',
        'phi_customer_insured_amount',
        'account_invoice_section_shipment',
        'sale_two_level_discounts',
        'quadra_export_ascii',
        'account_move_csv_import',
    ],
    "data": [
        'security/ir.model.access.csv',
        'views/mrp_bom_views.xml',
        'report/report_mrporder.xml',
        'report/report_invoice.xml',
        'report/stock_picking.xml',
        'report/report_purchase_order.xml',
        'report/report_sale_order.xml',
        'report/stock_report_deliveryslip.xml',
        'views/sale_order_views.xml',
        'views/product_template.xml',
    ]
}
