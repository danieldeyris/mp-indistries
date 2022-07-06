# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    picking_volume = fields.Float("Volume", compute="_compute_picking_volumepoids")
    picking_weight = fields.Float("Poids", compute="_compute_picking_volumepoids")

    def _compute_picking_volumepoids(self):
        for picking in self:
            picking.picking_volume = 0
            picking.picking_weight = 0
            for line in picking.move_line_ids:
                if line.product_id:
                    picking.picking_volume += (line.product_id.volume or 0.0) * line.qty_done
                    picking.picking_weight += (line.product_id.weight or 0.0) * line.qty_done

