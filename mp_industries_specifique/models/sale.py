# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_volume = fields.Float("Volume", compute="_compute_order_volumepoids")
    order_weight = fields.Float("Poids", compute="_compute_order_volumepoids")

    available_credit = fields.Monetary(related='partner_id.available_credit')
    credit_limit = fields.Monetary(related='partner_id.credit_limit')
    check_credit = fields.Boolean(related='partner_id.check_credit')

    def _compute_order_volumepoids(self):
        for order in self:
            order.order_volume = 0
            for line in order.order_line:
                order.order_volume += (line.product_id.volume or 0.0) * line.product_uom_qty
                order.order_weight += (line.product_id.weight or 0.0) * line.product_uom_qty

