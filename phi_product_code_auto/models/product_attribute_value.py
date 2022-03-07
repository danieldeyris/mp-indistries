from odoo import models,fields


class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    code_short = fields.Char(string='Code Court', help="Short Code for product SKU calculation")
