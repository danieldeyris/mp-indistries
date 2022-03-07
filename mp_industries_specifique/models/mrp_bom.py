# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class MrpBomLineDecoupe(models.Model):
    _name = 'mrp.bom.line.decoupe'
    _description = 'Découpe'

    bom_line_id = fields.Many2one("mrp.bom.line", "Ligne nomenclature",  ondelete='cascade')
    name = fields.Char("Description")
    qty = fields.Float("Quantité")


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    decoupe_ids = fields.One2many('mrp.bom.line.decoupe', 'bom_line_id', string='Découpes')

