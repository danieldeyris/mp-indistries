# See LICENSE file for full copyright and licensing details.

{
    # Module information
    'name': 'Catalog Pricelist Report',
    'category': 'Report',
    'summary': 'Generated the Product Catalog Report.',
    'description': 'Product Catalog report with Barcode, Image and \
     Stock Availability and Incoming Stock.\
      Catalog Product, Barcode, Image catalog report.',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'sequence': 1,
    # Author
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependencies
    'depends': ['sale_management', 'stock', 'purchase', 'product'],

    # Views
    'data': ['wizard/catalog_pricelist_wizard_view.xml',
             'report/catalog_report_view.xml',
             'report/report_registration.xml',
             'security/ir.model.access.csv',
             ],
    'images': ['static/description/banner_icon.jpg'],
    # Techical
    'installable': True,
    'auto_install': False,
    'price': 29,
    'currency': 'EUR',
}
