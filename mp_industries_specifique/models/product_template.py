# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _set_weight(self):
        for template in self:
            template.product_variant_ids.weight = template.weight

    @api.depends('product_variant_ids', 'product_variant_ids.weight')
    def _compute_weight(self):
        pass

    @api.depends('product_variant_ids', 'product_variant_ids.volume')
    def _compute_volume(self):
        pass

    def _set_volume(self):
        for template in self:
            template.product_variant_ids.volume = template.volume