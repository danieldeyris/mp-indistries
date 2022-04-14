{
    "name": "phidias : Two level discounts in Sales & Customer Invoice",
    "category": 'Sales',
    "summary": """
        Two level discounts in Sales order line and customer invoice line. 
    """,
    "sequence": 1,
    "author": "Phidias",
    "website": "http://www.phidias.fr/",
    "version": '14.0.0.0',
    "depends": ['sale_management', 'account'],
    "data": [
        'views/sale_view.xml',
        'views/account_move_view.xml',
        'report/sale_order_report_templates.xml',
        'report/invoice_report.xml',
        'views/sale_order_views_portal.xml',
    ],
}
