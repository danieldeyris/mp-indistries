# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_default_code_auto = fields.Boolean("Default Code Auto", compute="_compute_is_default_code_auto")

    @api.onchange('categ_id')
    def _compute_is_default_code_auto(self):
        for template in self:
            categ_sequence = self.categ_id.get_category_sequence()
            template.is_default_code_auto = (categ_sequence != False)

    @api.depends('product_variant_ids', 'product_variant_ids.default_code')
    def _compute_default_code(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                if not template.default_code:
                    template.default_code = template.product_variant_ids.default_code
            else:
                for variant in template.product_variant_ids.filtered(lambda var: not var.default_code):
                    variant.default_code = variant.generate_product_code()

    @api.onchange('categ_id')
    def _onchange_categ_id_default_code(self):
        for template in self:
            categ_old = template._origin.categ_id
            categ_sequence = template.categ_id.get_category_sequence()
            prefix = template.categ_id.get_category_prefix()
            separator = template.categ_id.get_category_separator()

            if categ_old:
                categ_sequence_old = categ_old.get_category_sequence()
                prefix_old = categ_old.get_category_prefix()
                separator_old = categ_old.get_category_separator()

                if categ_sequence != categ_sequence_old or prefix != prefix_old or separator != separator_old:
                    template.default_code = False

    def _set_default_code(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                return super(ProductTemplate, self)._set_default_code()
            else:
                for product in template.product_variant_ids:
                    product.default_code = product.generate_product_code()

    def generate_product_code(self, force=False):
        self.ensure_one()
        categ_sequence = self.categ_id.get_category_sequence()
        if (not self.default_code or force) and categ_sequence:
            separator = self.categ_id.get_category_separator()
            prefix = self.categ_id.get_category_prefix()
            prefix = prefix + separator if prefix else ""
            return prefix + categ_sequence.next_by_id()

    @api.model
    def create(self, vals):
        if 'default_code' not in vals or not vals.get('default_code'):
            categ = self.env['product.category'].browse(vals.get("categ_id"))
            categ_sequence = categ.get_category_sequence()
            if categ_sequence:
                separator = categ.get_category_separator()
                prefix = categ.get_category_prefix()
                prefix = prefix + separator if prefix else ""
                vals['default_code'] = prefix + categ_sequence.next_by_id()
        return super().create(vals)

    def write(self, vals):
        if 'default_code' not in vals or not vals.get('default_code'):
            for product in self:
                if not product.default_code or ('default_code' in vals and not vals.get('default_code')):
                    if vals.get('categ_id'):
                        categ = self.env['product.category'].browse(vals.get("categ_id"))
                    else:
                        categ = product.categ_id
                    categ_sequence = categ.get_category_sequence()
                    if categ_sequence:
                        separator = categ.get_category_separator()
                        prefix = categ.get_category_prefix()
                        prefix = prefix + separator if prefix else ""
                        vals['default_code'] = prefix + categ_sequence.next_by_id()
        return super().write(vals)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def generate_product_code(self):
        self.ensure_one()
        code_variant_auto = self.product_tmpl_id.categ_id.get_code_variant_auto()
        if code_variant_auto:
            if self.product_tmpl_id.default_code:
                code_short = []
                separator = self.product_tmpl_id.categ_id.get_category_separator()
                for product_template_attribute_value in self.product_template_attribute_value_ids:
                    code = product_template_attribute_value.product_attribute_value_id.code_short or product_template_attribute_value.product_attribute_value_id.name
                    if code:
                        code_short.append(code)
                if len(code_short):
                    return self.product_tmpl_id.default_code + separator + separator.join(code_short)
                else:
                    return self.product_tmpl_id.default_code
            else:
                return False
        else:
            return self.default_code
