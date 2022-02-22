# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    decoupe_ids = fields.One2many('stock.move.decoupe', 'move_id', string='Découpes', compute='_compute_decoupe_ids', store=True)

    def action_show_decoupe(self):
        self.ensure_one()
        action = super().action_show_details()
        action['views'] = [(self.env.ref('mp_industries_specifique.view_stock_move_operations_decoupe').id, 'form')]
        return action

    @api.depends('bom_line_id', 'raw_material_production_id.product_qty')
    def _compute_decoupe_ids(self):
        for move in self:
            move.decoupe_ids.unlink()
            if move.bom_line_id:
                for decoupe in move.bom_line_id.decoupe_ids:
                    vals = {
                        'move_id': move.id,
                        'name': decoupe.name,
                        'qty': decoupe.qty * move.raw_material_production_id.product_qty,
                    }
                    self.env["stock.move.decoupe"].create(vals)


class StockMoveDecoupe(models.Model):
    _name = 'stock.move.decoupe'
    _description = 'Découpe'

    move_id = fields.Many2one("stock.move", "Ligne", ondelete='cascade')
    name = fields.Char("Description")
    qty = fields.Float("Quantité")




