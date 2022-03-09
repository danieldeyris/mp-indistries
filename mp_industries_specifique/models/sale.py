# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_volume = fields.Float("Volume", compute="_compute_order_volume")

    def _compute_order_volume(self):
        for order in self:
            order.order_volume = 0
            for line in order.order_line:
                order.order_volume += (line.product_id.volume or 0.0) * line.product_uom_qty
