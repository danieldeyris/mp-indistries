# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    @api.onchange('route_id')
    def _compute_defalut_suppplier(self):
        for orderpoint in self:
            if orderpoint.show_supplier and not orderpoint.supplier_id:
                orderpoint.supplier_id = orderpoint.product_id._select_seller(quantity=1.0)

    @api.model
    def create(self, vals):
        result = super(Orderpoint, self).create(vals)
        return result

    def write(self, vals):
        result = super(Orderpoint, self).write(vals)
        if 'route_id' in vals:
            self._compute_defalut_suppplier()
        return result