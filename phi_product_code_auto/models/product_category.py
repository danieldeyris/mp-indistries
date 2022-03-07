# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code_prefix = fields.Char(
        string="Prefix for Product Internal Reference",
        help="Prefix used to generate the internal reference for products "
             "created with this category. If blank the "
             "default sequence will be used.",
    )

    code_separator = fields.Char(
        string="separator for Product Internal Reference",
        help="separator used to generate the internal reference for products "
             "created with this category. If blank the "
             "separator is '-'.",
    )

    code_sequence = fields.Many2one("ir.sequence", "Code Sequence")

    code_variant_auto = fields.Boolean("Code variant auto", default=True)

    def get_category_prefix(self):
        self.ensure_one()
        categ = self.env['product.category'].search([('id', 'parent_of', self.id), ('code_prefix', '!=', False)], order='id desc', limit=1)
        return categ.code_prefix if categ else False

    def get_category_separator(self):
        self.ensure_one()
        categ = self.env['product.category'].search([('id', 'parent_of', self.id), ('code_separator', '!=', False)], order='id desc', limit=1)
        return categ.code_separator if categ else '-'

    def get_category_sequence(self):
        self.ensure_one()
        categ = self.env['product.category'].search([('id', 'parent_of', self.id), ('code_sequence', '!=', False)], order='id desc', limit=1)
        return categ.code_sequence if categ else False

    def get_code_variant_auto(self):
        self.ensure_one()
        categ = self.env['product.category'].search([('id', 'parent_of', self.id)], order='id desc', limit=1)
        return categ.code_variant_auto