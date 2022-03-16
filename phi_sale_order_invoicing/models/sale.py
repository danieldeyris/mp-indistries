# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from itertools import groupby
from odoo.exceptions import AccessError, UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_mode = fields.Selection(related="partner_invoice_id.invoicing_mode")

    def _get_invoice_grouping_keys(self):
        for order in self:
            if order.invoicing_mode == 'reference':
                return ['company_id', 'partner_id', 'currency_id', 'ref']
            else:
                return super(SaleOrder, self)._get_invoice_grouping_keys()

    def _create_invoices_from_pickings(self, grouped=True, final=True, date=None):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        # 1) Create invoices.
        invoice_vals_list = []
        invoiced_line_service = self.env["sale.order.line"]
        invoice_item_sequence = 0 # Incremental sequencing to keep the lines order on the invoice.
        for order in self:

            down_payment_section_added = False

            if not any(picking.state == 'done' for picking in order.picking_ids):
                continue

            order = order.with_company(order.company_id)
            current_section_vals = None
            down_payments = order.env['sale.order.line']

            invoiceable_lines = order._get_invoiceable_lines(final)

            if not any(not line.display_type for line in invoiceable_lines):
                continue

            for picking in order.picking_ids.filtered(lambda p: p.state == 'done'):
                invoice_vals = order._prepare_invoice()
                invoice_vals["ref"] = picking.name
                invoice_line_vals = []
                for line in invoiceable_lines:
                    if not len(line.move_ids):
                        if line not in invoiced_line_service and line.is_downpayment:
                            # Create a dedicated section for the down payments
                            # (put at the end of the invoiceable_lines)
                            invoice_line_vals.append(
                                (0, 0, order._prepare_down_payment_section_line(
                                    sequence=invoice_item_sequence,
                                )),
                            )
                            down_payment_section_added = True
                            invoice_item_sequence += 1
                            invoice_line_vals.append(
                                (0, 0, line._prepare_invoice_line(
                                    sequence=invoice_item_sequence,
                                )),
                            )
                            invoiced_line_service |= line
                        else:
                            if line not in invoiced_line_service:
                                invoice_line_vals.append(
                                    (0, 0, line._prepare_invoice_line(
                                        sequence=invoice_item_sequence,
                                    )),
                                )
                                invoiced_line_service |= line
                        invoice_item_sequence += 1
                    else:
                        for move in line.move_ids:
                            if move.picking_id == picking and move.state == 'done':
                                line_invoice = line._prepare_invoice_line(sequence=invoice_item_sequence, )
                                line_invoice["quantity"] = move.product_uom_qty
                                invoice_line_vals.append((0, 0, line_invoice),)

                if len(invoice_line_vals):
                    invoice_vals['invoice_line_ids'] += invoice_line_vals
                    invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            return

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            invoice_vals_list = sorted(
                invoice_vals_list,
                key=lambda x: [
                    x.get(grouping_key) for grouping_key in invoice_grouping_keys
                ]
            )
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['payment_reference'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _prepare_invoice_line(self, **optional_values):
        res = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        self.ensure_one()
        if self.order_id.invoicing_mode == 'shipment':
            pass
        return res

