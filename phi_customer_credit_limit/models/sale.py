# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    exceeded_amount = fields.Float('Exceeded Amount', default=0, copy=False)
    credit_limit_force_reason = fields.Char("Credit limit force reason", copy=False)

    state = fields.Selection(selection_add=[('credit_limit', 'Credit limit')], ondelete={'credit_limit': 'set default'})

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        partner_id = self.partner_id
        if self.partner_id.parent_id:
            partner_id = self.partner_id.parent_id

        if partner_id:
            if partner_id.credit_limit_on_hold:
                msg = _("Customer %s is on credit limit hold.") % partner_id.name
                return {'warning': {'title': _('Credit Limit On Hold'), 'message': msg}}

    def action_force_credit(self):
        action = self.env["ir.actions.actions"].sudo()._for_xml_id("phi_customer_credit_limit.action_customer_limit_wizard")
        return action

    def confirm_force_credit(self):
        return super(SaleOrder, self).action_confirm()

    def action_confirm(self):
        for order in self:
            if order.partner_id.check_credit and order.amount_total > order.partner_id.available_credit:
                order.state = 'credit_limit'
                order.exceeded_amount = order.partner_id.to_invoice_amount + order.partner_id.draft_invoice_lines_amount + order.partner_id.credit + order.amount_total - order.partner_id.credit_limit
                message = _("Sale order %s for customer %s require your Credit Limit Approval.") % (order.name, order.partner_id.name)
                manager_group_id = self.env.ref('sales_team.group_sale_manager').ids
                browse_group = self.env['res.groups'].browse(manager_group_id)
                for user in browse_group.users:
                    existing_activity = self.env['mail.activity'].search([
                        ('res_id', '=', order.id),
                        ('res_model_id', '=', self.env['ir.model']._get('sale.order').id),
                        ('activity_type_id', '=', self.env.ref('mail.mail_activity_data_todo').id),
                        ('summary', '=', message)])
                    if not existing_activity:
                        self.env['mail.activity'].create({
                            'summary': message,
                            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                            'res_model_id': self.env['ir.model']._get('sale.order').id,
                            'res_id': order.id,
                            'user_id': user.id
                        })

                return True
            else:
                res = super(SaleOrder, self).action_confirm()
        return res
