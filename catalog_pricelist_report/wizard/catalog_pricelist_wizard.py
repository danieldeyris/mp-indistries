# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class CatalogPricelistReport(models.TransientModel):
    _name = "catalog.pricelist.report.wizard"
    _description = 'Catalog Pricelist Report'

    pricelist_id = fields.Many2one('product.pricelist')
    language_id = fields.Many2one('res.lang', string='Language')
    custom_title = fields.Char(string="Custom Title")
    qty_1 = fields.Integer(string="Quantity 1", default=1)
    qty_2 = fields.Integer(string="Quantity 2")
    qty_3 = fields.Integer(string="Quantity 3")
    header = fields.Boolean(string="Print Header", default="1")
    print_images = fields.Boolean(string="Print Image")
    print_attributes = fields.Boolean(string="Print Attributes")
    attribute_bg_color = fields.Char(string="Attribute background Color")
    barcode_print = fields.Boolean(string="Print Barcode")
    barcode_type = fields.Selection([('codabar', 'Codabar'),
                                     ('codell', 'Code11'),
                                     ('code128', 'Code128'),
                                     ('ean13', 'EAN13'), ('ean8', 'EAN8'),
                                     ('extended39', 'Extended39'),
                                     ('extended93', 'Extended93'),
                                     ('fim', 'FIM'),
                                     ('i2of5', 'i2of5'),
                                     ('msi', 'MSI'),
                                     ('postnet', 'Postnet'),
                                     ('qr', 'QR'),
                                     ('standard39', 'Standard39'),
                                     ('standard93', 'Standard93'),
                                     ('usps_4stater', 'USPS_4Stater')],
                                    default="ean13", string="Barcode Type")
    barcode_height = fields.Integer(string="Barcode Height", default='200')
    barcode_width = fields.Integer(string="Barcode Width", default='50')
    available_quantity = fields.Boolean(string="Print Available Quantity")
    incoming_quantity = fields.Boolean(string="Print Incoming Quantity")
    image = fields.Binary(string='Add Logo In Report')

    def print_report(self):
        active_ids = self.env.context.get('active_ids', [])
        data = self.read()[0]
        datas = {
            'ids': active_ids,
            'model': 'product.product',
            'form': data,
        }
        return self.env.ref(
            'catalog_pricelist_report.action_catalog_report').report_action(
            [], data=datas)
